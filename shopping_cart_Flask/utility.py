from datetime import datetime

def success(data=None, total=0):
    if data is None:
        return {'message': 'success'}, 200
        
    return {
        'message': 'success',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }, 200


def failure(data=None):
    if data is None:
        return {'message': 'failure'}, 500
    
    return {
        'message': 'failure',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }, 500


def total(data=None,total=0):
    return {
        'message': 'success',
        'data': data,
        'totalPrice':total,
        'datatime': datetime.utcnow().isoformat()
    }, 200