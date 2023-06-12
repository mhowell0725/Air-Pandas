import data_cleaning
from sqlalchemy import create_engine

'''
This script is a sample of how to creates a SQL database from the CSV files we had from the AQS API and the Census API.

It will interact with the data_cleaning.py file, which contains the functions query and to clean the data by chunk, and store them in the database.

To replicate our process, first obtain the CSV files from the AQS API and the Census API,
then change the file paths and names in the main() function.

For AQS data, we only handle the sampleData, not the dailyData. (i.e. this handle any AQS dataframe with hourly data)

You can also change the name of the output database

'''


def main():

    output_database_name = 'airpandas_1.sqlite' ## YOU CAN CHANGE THIS NAME
    engine = create_engine(f'sqlite:///{output_database_name}')

    
    census_file_name = {
        "Race" : r"database\census_data_RACE_2009-2021.csv",
        "Income" : r"database\census_data_INCOME_AND_BENEFITS_2009-2021.csv",
        "Education" : r"database\census_data_EDUCATIONAL_ATTAINMENT_2009-2021.csv",
        "Employment" : r"database\census_data_EMPLOYMENT_STATUS_2009-2021.csv",
        "Heating" : r"database\census_data_HOUSE_HEATING_FUEL_2009-2021.csv",
        "Occupation" : r"database\census_data_OCCUPATION_2009-2021.csv",
        "Commute" : r"database\census_data_COMMUTING_TO_WORK_2009-2021.csv",
        "Industry" : r"database\census_data_INDUSTRY_2009-2021.csv",
        "Poverty" : r"database\census_data_PERCENTAGE_OF_FAMILIES_AND_PEOPLE_WHOSE_INCOME_IN_THE_PAST_12_MONTHS_IS_BELOW_THE_POVERTY_LEVEL_2009-2021.csv",

    }

    for table_name, file_name in census_file_name.items():
        data_cleaning.query_census(file_name, engine, table_name)

    file_names = [r'database\2009_2014.6_CA_PM2.5_samples.csv', r'database\2014.6_2021_CA_PM2.5_samples.csv']
    data_cleaning.process_csv_in_chunks(file_names, 10000, engine, 'PM25')



if __name__ == '__main__':
    main()

