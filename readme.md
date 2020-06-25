# [Nina](https://portal.ninamob.com/)

- [Chosen Data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
- **[API URL](https://45xzvibz04.execute-api.us-east-1.amazonaws.com/default/confirmed_cases)**

Data chosen was a set of time series tables where each csv file is a day since january 2020 with updates on confirmed, deceased and recovered cases of COVID-19 by country/region and province/state.

First the [Spider](/spider) was developed to crawl the web page and retrieve all new csvs files. Spider is triggered everyday by CloudWatch event and stores raw csv files in a S3 bucket.

Then the [Extractor](/extractor) crops and cleans the data provided by the spider and stores it in another S3 folder. This folder feeds an Athena table that contains the time series data with only the fields: `country/region: string`, `province/state: string`, `confirmed: int`, `recovered: int`, `deaths: int` and `date: date`

The [Aggregator function](/aggregator) queries the covid table to sum recent values and get update data about each country. Then stores the queried data in another S3 folder daily (CloudWatch event again) and then deletes and recriates the aggregated table on Athena.

The aggregated table is used by the API endpoint to provide the total confirmed cases by country through the [confirmed_cases lambda function](/confirmed)

> :warning: Not in this repo but in order to run some of these lambda functions, some lambda layers were created, mainly containing python libraries like pyyaml and requests

![diagram](/misc/Nina.png)

## Task

Build a small data-oriented solution in any cloud you want:

1. Get together and get to know each other
2. Structure your work and split the work, so you can implement this as a mini team
3. Choose a storage service that provides an optimal foundation for the data-driven
   solution. Setup the storage platform with DevOps principles like infrastructure as a
   code. The cloud automation framework is free of choice, too.
4. Upload sample data from any sample data source you want for this exercise, some samples can be found here:
   - [AWS registry](https://registry.opendata.aws/)
   - [Forbes](https://www.forbes.com/sites/bernardmarr/2016/02/12/big-data-35-brilliant-and-free-data-sources-for-2016/#28777d49b54d)
   - [DataQuest](https://www.dataquest.io/blog/free-datasets-for-projects/)
   - [COVID-19](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
     to help you:
     [AWS samples](https://github.com/aws-samples/aws-research-workshops/blob/master/notebooks/escience_series/using_s3_and_analytics.ipynb)
5. Index the data and create a meta data catalogue that make it possible to query the data
   with SQL
6. Create an aggregation data set inside of a new data storage area, it can be a SUM,
   AVERAGE, any aggregation you wish you can explain. The application that is writing
   the aggregation data set should be deployed inside AWS. Index this data and make it
   queryable via SQL.
7. Implement a service in Python to show one of the data fields stored in the data set
8. Check-in in the code to a public git repo, using Github or Gitlab
9. Deploy it to a serverless container (e.g. Lambda)
10. Send us the link of the Git repo with the service and the URL of the service showing the
    data field.

## Architecture

- Draw the architecture project did by you to this project. You can use [AWS Architecture Diagrams Online](https://aws.amazon.com/architecture/icons/)
