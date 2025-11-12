"""
Minimal Vercel handler for testing
Use this to verify the basic handler works before adding complexity
"""

import json

def handler(request):
    """Minimal handler that should always work"""
    try:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'ok',
                'message': 'Handler is working'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

