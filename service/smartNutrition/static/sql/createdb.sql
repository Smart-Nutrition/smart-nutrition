
CREATE TABLE User (
	user_id integer AUTO_INCREMENT PRIMARY KEY,
	username varchar(20) NOT NULL,
	firstname varchar(20) NOT NULL,
	lastname varchar(20) NOT NULL,
	password varchar(256) NOT NULL, --Hash of password
	email varchar(40) NOT NULL,
	diet_id integer NOT NULL
	);

CREATE TABLE Trip (
	trip_id integer AUTO_INCREMENT PRIMARY KEY,
	user_id integer NOT NULL,
	trip_date timestamp NOT NULL,
	sum_calories decimal NOT NULL,
	sum_protein decimal NOT NULL,
	sum_fat decimal NOT NULL,
	sum_trans_fat decimal NOT NULL,
	sum_sat_fat decimal NOT NULL,
	sum_carb decimal NOT NULL,
	sum_starch decimal NOT NULL,
	sum_sucrose decimal NOT NULL,
	sum_glucose decimal NOT NULL,
	sum_frucose decimal NOT NULL,
	sum_lactose decimal NOT NULL,
	sum_maltose decimal NOT NULL,
	sum_alcohol decimal NOT NULL,
	sum_water decimal NOT NULL,
	sum_caffeine decimal NOT NULL,
	sum_sugar decimal NOT NULL,
	sum_fiber decimal NOT NULL,
	sum_calcium decimal NOT NULL,
	sum_iron decimal NOT NULL,
	sum_magnesium decimal NOT NULL,
	sum_phosphorus decimal NOT NULL,
	sum_potassium decimal NOT NULL,
	sum_sodium decimal NOT NULL,
	sum_zinc decimal NOT NULL,
	sum_copper decimal NOT NULL,
	sum_flouride decimal NOT NULL,
	sum_manganese decimal NOT NULL,
	sum_selenium decimal NOT NULL,
	sum_vit_a decimal NOT NULL,
	sum_vit_b6 decimal NOT NULL,
	sum_vit_b12 decimal NOT NULL,
	sum_vit_c decimal NOT NULL,
	sum_vit_d decimal NOT NULL,
	sum_vit_d2 decimal NOT NULL,
	sum_vit_d3 decimal NOT NULL,
	sum_vit_e decimal NOT NULL,
	sum_vit_k decimal NOT NULL,
	sum_carotene_alpha decimal NOT NULL,
	sum_carotene_beta decimal NOT NULL,
	sum_thiamin decimal NOT NULL,
	sum_riboflavin decimal NOT NULL,
	sum_niacin decimal NOT NULL,
	sum_cholesterol decimal NOT NULL
	);

CREATE TABLE Diet (
	diet_id integer AUTO_INCREMENT PRIMARY KEY,
	calories integer NOT NULL,
	goal_calories decimal NOT NULL,
	goal_protein decimal NOT NULL,
	goal_fat decimal NOT NULL,
	goal_trans_fat decimal NOT NULL,
	goal_sat_fat decimal NOT NULL,
	goal_carb decimal NOT NULL,
	goal_starch decimal NOT NULL,
	goal_sucrose decimal NOT NULL,
	goal_glucose decimal NOT NULL,
	goal_frucose decimal NOT NULL,
	goal_lactose decimal NOT NULL,
	goal_maltose decimal NOT NULL,
	goal_alcohol decimal NOT NULL,
	goal_water decimal NOT NULL,
	goal_caffeine decimal NOT NULL,
	goal_sugar decimal NOT NULL,
	goal_fiber decimal NOT NULL,
	goal_calcium decimal NOT NULL,
	goal_iron decimal NOT NULL,
	goal_magnesium decimal NOT NULL,
	goal_phosphorus decimal NOT NULL,
	goal_potassium decimal NOT NULL,
	goal_sodium decimal NOT NULL,
	goal_zinc decimal NOT NULL,
	goal_copper decimal NOT NULL,
	goal_flouride decimal NOT NULL,
	goal_manganese decimal NOT NULL,
	goal_selenium decimal NOT NULL,
	goal_vit_a decimal NOT NULL,
	goal_vit_b6 decimal NOT NULL,
	goal_vit_b12 decimal NOT NULL,
	goal_vit_c decimal NOT NULL,
	goal_vit_d decimal NOT NULL,
	goal_vit_d2 decimal NOT NULL,
	goal_vit_d3 decimal NOT NULL,
	goal_vit_e decimal NOT NULL,
	goal_vit_k decimal NOT NULL,
	goal_carotene_alpha decimal NOT NULL,
	goal_carotene_beta decimal NOT NULL,
	goal_thiamin decimal NOT NULL,
	goal_riboflavin decimal NOT NULL,
	goal_niacin decimal NOT NULL,
	goal_cholesterol decimal NOT NULL
	);

CREATE TABLE Food (
	sequence_num integer PRIMARY KEY,
	trip_id integer NOT NULL,
	food_id integer NOT NULL,
	food_name varchar(100) NOT NULL
	);

CREATE TABLE Provider (
	id integer AUTO_INCREMENT PRIMARY KEY,
	user_id integer NOT NULL,
	provider_name varchar(20) NOT NULL,
	username varchar(40) NOT NULL,
	password varchar(40) NOT NULL
	);

-- source (path of insert file)
