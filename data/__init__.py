from .diseases import DISEASES, CATEGORIES
from .medical_expansion import MEDICAL_EXPANSION_CATEGORIES, MEDICAL_EXPANSION_DISEASES
from .red_flags import RED_FLAGS, EMERGENCY_NUMBERS
from .first_aid import FIRST_AID
from .definitions import DEFINITIONS
from .faq import FAQ, WELLNESS_TIPS
from .hospital_finder import (
    OVERLAPPING_CONDITIONS,
    check_needs_hospital_recommendation,
    HOSPITAL_RECOMMENDATION_TEXT,
    find_nearby_hospitals,
)

DISEASES.update(MEDICAL_EXPANSION_DISEASES)
CATEGORIES.update(MEDICAL_EXPANSION_CATEGORIES)
