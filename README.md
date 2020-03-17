# Serverless Pipeline with Amazon Web Services Lambda Functions
This repo contains the files for Project 4 for DSBA 6190 (Intro to Cloud Computing) at UNC Charlotte for the Spring 2020 semester. The goal of this project was to construct a serverless process flow using Amazon Lambda functions. Furthermore, this project also involved the integration of several different AWS services, including S3 (storage), DynamoDB (non-relational database), SQS (messaging), and Comprehend (natural language processing).

# Process Flow
The following diamgram outlines the general process flow, with all of the AWS components represented. 
![](https://user-images.githubusercontent.com/38056064/76878084-b3b3e000-684a-11ea-9dac-b425bc3f91eb.png)
Created with CloudCraft.co

## Set-Up
As precurser to the process flow functioning a table was populated in DynamoDB. The table was simple, just six entries of a single variable. For this project I chose well known 100+ mile Ultra races, but the actual content is not important. All that is necessary is that the items in the DyanmoDB have a wikipedia entry, and that the entry format in the DynamoDB table matches the wikipedia entry. We'll get to why when discussing specific lambda function actions.

## Lambda Functions
The core of this pipeline is the two lambda functions. For this project they were referred to as Producer and Consumer functions, respectively.

### Producer
The Producer function read data into the pipeline and then send out a SQS message, stating what had been read. In this case, the function reads row by row from a DynamoDB table. 

*Note*: While not documented in the repo, in the AWS pipeline the function is triggered by a CloudWatch Event setup to activate once a minute.

### Consumer
The Consumer function reads the SQS message sent by the Producer function, processes information contained in the message, and then saves the processed data as a CSV file in a designated S3 bucket. 

To process the data, the function extracts the body of the SQS event payload received by the lambda function. In this case, the event body has the following structure, in JSON format : {Race:<Race Name>}. Upon reading the SQS event payload, the Consumer function takes the following actions:
  1. Extract **body** entry from SQS payload.
  2. Using the Wikipedia API, download the first sentence of the Wikipedia entry for <Race Name>.
  3. Detect the entities in Wikipedia sample, using AWS Comprehend, a Natural Language Processing service.
  4. Write the detected entities to a pandas dataframe, and then save the dataframe as a CSV file in a S3 bucket.

*Note*: While not documented in the repo, in the AWS pipeline the function is triggered by a SQS event setup to read the SQS queue being populated by the Procedure function. The Consumer function activates upon reading a new SQS message.

# Output Example
To clearly show the pipeline results, the following is the input and output for the Vermont 100 Mile Endurance Run, one of the items in the initial DynamoDB database. As you can see, AWS comprehend is able to detect and identify type for the entites in the first sentance of the Wikipedia Entry.

## Wikipedia Entry
![](https://user-images.githubusercontent.com/38056064/76873516-39805d00-6844-11ea-9523-a4d97f8fe7c4.png)

## Detect Entity Results
![](https://user-images.githubusercontent.com/38056064/76869699-0f786c00-683f-11ea-859b-1e4bed0d9285.png)
