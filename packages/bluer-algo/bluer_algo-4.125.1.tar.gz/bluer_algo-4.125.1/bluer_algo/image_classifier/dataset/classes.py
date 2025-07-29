import copy
import pandas as pd
from typing import Dict, Tuple

from bluer_objects import objects, file
from bluer_objects.metadata import post_to_object
from bluer_objects.logger.image import log_image_grid
from bluer_objects.metadata import get_from_object

from bluer_algo.host import signature
from bluer_algo.logger import logger


class ImageClassifierDataset:
    def __init__(
        self,
        dict_of_classes: Dict = {},
    ):
        self.list_of_subsets = ["train", "test", "eval"]

        self.df = pd.DataFrame(
            columns=[
                "filename",
                "class_index",
                "subset",
            ]
        )

        self.dict_of_classes = dict_of_classes.copy()

    def add(
        self,
        filename: str,
        class_index: int,
        subset: str,
    ):
        self.df.loc[len(self.df)] = {
            "filename": file.name_and_extension(filename),
            "class_index": class_index,
            "subset": subset,
        }

    def as_str(self, what="subsets") -> str:
        count = self.count

        if what == "classes":
            return "{} class(es): {}".format(
                self.class_count,
                ", ".join(
                    [
                        "{}: {} [%{:.1f}]".format(
                            self.dict_of_classes[class_index],
                            class_count,
                            class_count / count * 100,
                        )
                        for class_index, class_count in self.dict_of_class_counts.items()
                    ]
                ),
            )

        if what == "subsets":
            return "{} subset(s): {}".format(
                len(self.list_of_subsets),
                ", ".join(
                    [
                        "{}: {} [%{:.1f}]".format(
                            subset, subset_count, subset_count / count * 100
                        )
                        for subset, subset_count in self.dict_of_subsets.items()
                    ]
                ),
            )

        return f"{what} not found."

    @property
    def class_count(self) -> int:
        return len(self.dict_of_classes)

    @property
    def count(self) -> int:
        return len(self.df)

    @property
    def dict_of_class_counts(self) -> Dict[int, int]:
        return {
            class_index: self.df[self.df["class_index"] == class_index].shape[0]
            for class_index in self.dict_of_classes.keys()
        }

    @property
    def dict_of_subsets(self) -> Dict[str, int]:
        return {
            subset_name: self.df[self.df["subset"] == subset_name].shape[0]
            for subset_name in self.list_of_subsets
        }

    @staticmethod
    def load(
        object_name: str,
        log: bool = True,
    ) -> Tuple[bool, "ImageClassifierDataset"]:
        dataset = ImageClassifierDataset()

        success, dataset.df = file.load_dataframe(
            objects.path_of(
                object_name=object_name,
                filename="metadata.csv",
            ),
            log=log,
        )
        if not success:
            return False, dataset

        metadata = get_from_object(
            object_name=object_name,
            key="dataset",
        )
        dataset.dict_of_classes = metadata["classes"]

        logger.info(dataset.as_str("subsets"))
        logger.info(dataset.as_str("classes"))

        return (
            dataset.log_image_grid(
                object_name=object_name,
                log=log,
            ),
            dataset,
        )

    def log_image_grid(
        self,
        object_name: str,
        log: bool = True,
        verbose: bool = False,
    ) -> bool:
        df = self.df.copy()

        df["title"] = df.apply(
            lambda row: "#{}: {} @ {}".format(
                row["class_index"],
                self.dict_of_classes[row["class_index"]],
                row["subset"],
            ),
            axis=1,
        )

        return log_image_grid(
            df,
            objects.path_of(
                object_name=object_name,
                filename="grid.png",
            ),
            shuffle=True,
            header=[
                f"count: {self.count}",
                self.as_str("subsets"),
                self.as_str("classes"),
            ],
            footer=signature(),
            log=log,
            verbose=verbose,
            relative_path=True,
        )

    def save(
        self,
        object_name: str,
        metadata: Dict = {},
        log: bool = True,
    ) -> bool:
        logger.info(self.as_str("subsets"))
        logger.info(self.as_str("classes"))

        metadata_ = copy.deepcopy(metadata)
        metadata_["classes"] = self.dict_of_classes
        metadata_["class_count"] = self.class_count
        metadata_["count"] = self.count
        metadata_["subsets"] = self.dict_of_subsets

        if not file.save_csv(
            objects.path_of(
                object_name=object_name,
                filename="metadata.csv",
            ),
            self.df,
            log=log,
        ):
            return False

        if not post_to_object(
            object_name=object_name,
            key="dataset",
            value=metadata_,
        ):
            return False

        if not self.log_image_grid(
            object_name=object_name,
            log=log,
        ):
            return False

        logger.info(f"{self.count} record(s) -> {object_name}")

        return True
