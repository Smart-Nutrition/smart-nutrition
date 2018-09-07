# Smart Nutrition
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/Smart-Nutrition/smart-nutrition.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Smart-Nutrition/smart-nutrition/context:javascript)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Smart-Nutrition/smart-nutrition.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Smart-Nutrition/smart-nutrition/context:python)

Tracks your nutrition, without you doing a thing.

## Important Note
This project is a webserver with multiple secret keys. The keys stored here are for example only and should not be used in a publicly-accessible web server. Please change the keys if deploying yourself.

For instance, you will need Nutritionix API keys, which must be obtained yourself.

### Security
This project was developed as a senior design project at the University of Michigan, and security was not the primary goal (in fact, it wasn't a goal at all). Therefore, this project contains multiple vulnerabilities that we will try to fix over time.

Since this project should not be used by "common folk", all security-sensitive bugs will be publicly available on the issue tracker. If you find a vulnerability that isn't listed on the issue tracker, please file a ticket (you may do so publicly).

## Instructions for Starting Smart Nutrition Service (Server + Site)
1. Clone repo
2. `cd service/`
3. `./configure.sh`
4. `source env/bin/activate`
5. `./run.sh`
6. Open web browser to localhost:8000

