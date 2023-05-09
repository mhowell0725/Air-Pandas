## Here is the repository for Air-Pandas!!

There is a growing body of literature detailing the relationship between the level of air pollution and the demography in different neighborhoods of Los Angeles (e.g. Jiang and Yang 2022). Despite their substantial implications on the quality of life of millions of people, the majority of the discussions surrounding this issue have remained in an academic setting. In this project, we plan to increase accessibility to this body of knowledge. To do so, we will interpret the existing literature for demographic trends in Los Angeles and how they relate to real air quality records, create a database of historical Los Angeles air quality and demographic data, and visualize the relationship between demographic and air quality trends. These tasks will require working with large demographic and environmental datasets, creating and working with a SQL database, and communicating the findings through complex visualizations.


#### So far, we want to focus on data within *LA* or *California*


### Current issues regarding AQI:
1. Popular air quality measures include PM2.5, PM10, Ozone, CO, etc. Yet, NOT every site has all those measures throughout the time periods.
2. The location/geographic distribution of the sites are uneven -- need to think about ways to integrate with Census data based on geographic locations
3. We might want to query all the data into one *database* before analyzing; so we have to decide a time range and an area (i.e latitude and longitude range) and write query functions to collect them into separate catagories based on air quality parameters.