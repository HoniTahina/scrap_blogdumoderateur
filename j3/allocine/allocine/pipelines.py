# pipelines.py
from itemadapter import ItemAdapter


class CleanPipeline:
    def process_item(self, item, spider):
        a = ItemAdapter(item)

        if a.get("titre"):
            a["titre"] = a["titre"].strip()

        for champ in ("note_presse", "note_spectateurs"):
            valeur = a.get(champ)
            if valeur:
                try:
                    a[champ] = float(valeur.replace(",", "."))
                except (ValueError, AttributeError):
                    a[champ] = None

        return item