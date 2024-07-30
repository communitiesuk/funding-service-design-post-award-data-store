from random import shuffle

from faker import Faker
from faker.providers import BaseProvider, DynamicProvider

from data_store.const import ImpactEnum, LikelihoodEnum, ProximityEnum, RiskCategoryEnum

sign_off_role_provider = DynamicProvider(
    provider_name="sign_off_role",
    elements=["Section 151 Officer", "Chief Finance Officer", "Head of Finance", "Senior Responsible Owner"],
)

impact_provider = DynamicProvider(
    provider_name="impact",
    elements=[e.value for e in ImpactEnum],
)

likelihold_provider = DynamicProvider(
    provider_name="likelihood",
    elements=[e.value for e in LikelihoodEnum],
)

proximity_provider = DynamicProvider(
    provider_name="proximity",
    elements=[e.value for e in ProximityEnum],
)

risk_category_provider = DynamicProvider(
    provider_name="risk_category",
    elements=[e.value for e in RiskCategoryEnum],
)

risk_name_provider = DynamicProvider(
    provider_name="risk_name",
    elements=["Financial Risk", "Operational Risk", "Social Risk", "Environmental Risk"],
)

risk_owner_role_provider = DynamicProvider(
    provider_name="risk_owner_role",
    elements=["Risk Manager", "Surveyor", "Risk Assessor"],
)


class CustomProvider(BaseProvider):
    def sign_off_name(self):
        first_name = self.generator.first_name()
        last_name = self.generator.last_name()
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@testuser.com"
        return {"name": name, "email": email}

    def risk_register(self):
        consequences = self.generator.sentence(nb_words=12)
        full_desc = self.generator.sentence(nb_words=20)
        mitigation = self.generator.sentence(nb_words=10)

        short_description = self.generator.sentence(nb_words=6)
        risk_name = self.generator.word()

        return {
            "consequences": consequences,
            "full_desc": full_desc,
            "mitigation": mitigation,
            "short_description": short_description,
            "risk_name": risk_name,
        }


f = Faker(["en_GB"])
providers = [
    CustomProvider,
    sign_off_role_provider,
    impact_provider,
    likelihold_provider,
    proximity_provider,
    risk_category_provider,
    risk_name_provider,
    risk_owner_role_provider,
]

for item in providers:
    f.add_provider(item)


def shuffle_word(string):
    words = string.split()
    if words:
        first_word_list = list(words[0].lower())
        shuffle(first_word_list)
        words[0] = "".join(first_word_list).capitalize()
    return " ".join(words)
