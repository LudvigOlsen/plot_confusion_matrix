def get_templates():
    temps = Templates()

    # Blues
    temps.add(
        name="Blues 2-Class",
        num_classes=2,
        sums=False,
        settings_path="design_settings.blues_nc2_1.1.json",
        image_path="blues_nc2_1.1.png",
        collection="Blues 1",
    )
    temps.add(
        name="Blues 3-Class",
        num_classes=3,
        sums=False,
        settings_path="design_settings.blues_nc3_1.1.json",
        image_path="blues_nc3_1.1.png",
        collection="Blues 1",
    )
    temps.add(
        name="Blues 2-Class w/ Sums",
        num_classes=2,
        sums=True,
        settings_path="design_settings.blues_nc2_sums_1.1.json",
        image_path="blues_nc2_sums_1.1.png",
        collection="Blues 1",
    )
    temps.add(
        name="Blues 3-Class w/ Sums",
        num_classes=3,
        sums=True,
        settings_path="design_settings.blues_nc3_sums_1.1.json",
        image_path="blues_nc3_sums_1.1.png",
        collection="Blues 1",
    )

    # Greys
    temps.add(
        name="Greys 2-Class",
        num_classes=2,
        sums=False,
        settings_path="design_settings.greys_nc2_1.1.json",
        image_path="greys_nc2_1.1.png",
        collection="Greys 1",
    )
    temps.add(
        name="Greys 3-Class",
        num_classes=3,
        sums=False,
        settings_path="design_settings.greys_nc3_1.1.json",
        image_path="greys_nc3_1.1.png",
        collection="Greys 1",
    )
    temps.add(
        name="Greys 2-Class w/ Sums",
        num_classes=2,
        sums=True,
        settings_path="design_settings.greys_nc2_sums_1.1.json",
        image_path="greys_nc2_sums_1.1.png",
        collection="Greys 1",
    )
    temps.add(
        name="Greys 3-Class w/ Sums",
        num_classes=3,
        sums=True,
        settings_path="design_settings.greys_nc3_sums_1.1.json",
        image_path="greys_nc3_sums_1.1.png",
        collection="Greys 1",
    )

    # Turquoise
    # Greys
    temps.add(
        name="Turquoises 2-Class",
        num_classes=2,
        sums=False,
        settings_path="design_settings.turquoise_nc2_1.1.json",
        image_path="turquoise_nc2_1.1.png",
        collection="Turquoises 1",
    )
    temps.add(
        name="Turquoises 3-Class",
        num_classes=3,
        sums=False,
        settings_path="design_settings.turquoise_nc3_1.1.json",
        image_path="turquoise_nc3_1.1.png",
        collection="Turquoises 1",
    )
    temps.add(
        name="Turquoises 2-Class w/ Sums",
        num_classes=2,
        sums=True,
        settings_path="design_settings.turquoise_nc2_sums_1.1.json",
        image_path="turquoise_nc2_sums_1.1.png",
        collection="Turquoises 1",
    )
    temps.add(
        name="Turquoises 3-Class w/ Sums",
        num_classes=3,
        sums=True,
        settings_path="design_settings.turquoise_nc3_sums_1.1.json",
        image_path="turquoise_nc3_sums_1.1.png",
        collection="Turquoises 1",
    )

    return temps.get_templates()


class Templates:
    def __init__(self) -> None:
        self.templates = {}

    def get_templates(self) -> dict:
        return self.templates

    def add(
        self,
        name: str,
        num_classes: int,
        sums: bool,
        settings_path: str,
        image_path: str,
        collection: str,
    ) -> None:
        self.templates[name] = {
            "collection": collection,
            "num_classes": num_classes,
            "sums": sums,
            "settings": settings_path,
            "image": image_path,
        }
