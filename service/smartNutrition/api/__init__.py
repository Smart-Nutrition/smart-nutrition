"""API endpoints"""
from smartNutrition.api.app import login_api_route
from smartNutrition.api.app import logout_api_route
from smartNutrition.api.app import users_api_route
from smartNutrition.api.app import trip_api_route
from smartNutrition.api.app import summary_api_route
from smartNutrition.api.app import macronutrients_api_route
from smartNutrition.api.app import foodgroups_api_route
from smartNutrition.api.app import providers_api_route
from smartNutrition.api.app import provider_api_route
from smartNutrition.api.app import manual_trips_api_route
from smartNutrition.api.app import manual_trip_api_route
from smartNutrition.api.nutritionix import compute_trip_nutrition
from smartNutrition.api.nutritionix import ureg
