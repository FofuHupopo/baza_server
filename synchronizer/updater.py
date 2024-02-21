from .moy_sklad import MoySklad


class MoySkladUpdater(MoySklad):
    def quantity(self, modification_id: str, quantity: int):
        self.moysklad_patch(
            "MODIFICATION"
        )
