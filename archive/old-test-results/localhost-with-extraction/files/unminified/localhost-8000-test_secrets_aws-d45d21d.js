// Test file 1: AWS credentials (fake)
const AWS = require("aws-sdk");

// FAKE AWS Credentials - DO NOT USE IN PRODUCTION
const awsConfig = {
  accessKeyId: "AKIAIOSFODNN7EXAMPLE",
  secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  region: "us-east-1",
};

// Initialize AWS SDK
const s3 = new AWS.S3(awsConfig);

function uploadToS3(bucket, key, data) {
  const params = {
    Bucket: bucket,
    Key: key,
    Body: data,
  };

  return s3.upload(params).promise();
}

// API endpoint
const API_URL = "/api/v1/upload";
const API_KEY = "test-api-key-12345";

module.exports = { uploadToS3, API_URL };
