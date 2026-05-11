import json
import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ["TOPIC_ARN"]


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        claims = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("jwt", {})
            .get("claims", {})
        )

        groups = claims.get("cognito:groups", "")

        if "Admins" not in groups:
            return response(
                403, {"error": "Not authorized. Only admins can send events."}
            )

        body = json.loads(event.get("body", "{}"))

        title = body.get("title", "")
        date = body.get("date", "")
        message = body.get("message", "")

        if not title or not date or not message:
            return response(400, {"error": "Please fill in title, date, and message."})

        email_message = f"""
Event Announcement

Title: {title}
Date: {date}

Details:
{message}
"""

        sns.publish(
            TopicArn=TOPIC_ARN, Subject=f"Event Update: {title}", Message=email_message
        )

        return response(200, {"message": "Event announcement sent successfully!"})

    except Exception as e:
        return response(500, {"error": str(e)})
