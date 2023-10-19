def state_totals(company_name: str):
    return [
        {
            '$match': {
                'FACTORY.NAME': company_name
            }
        }, {
            '$unwind': {
                'path': '$LINE_ITEMS'
            }
        }, {
            '$group': {
                '_id': {
                    'NAME': '$FACTORY.NAME',
                    'CITY': '$FACTORY.CITY',
                    'STATE': '$FACTORY.STATE'
                },
                'totalSalesAmount': {
                    '$sum': {
                        '$toDecimal': '$LINE_ITEMS.PRICE'
                    }
                },
                'totalOrders': {
                    '$count': {}
                }
            }
        }, {
            '$addFields': {
                'locationId': '$_id.ID',
                'locationName': '$_id.NAME',
                'locationCity': '$_id.CITY',
                'locationState': '$_id.STATE',
                'locationZipCode': '$_id.ZIP_CODE'
            }
        }, {
            '$group': {
                '_id': '$locationState',
                'totalSalesAmount': {
                    '$sum': '$totalSalesAmount',
                },
                'totalOrders': {
                    '$sum': '$totalOrders'
                }
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }, {
            '$addFields': {'state': '$_id'}
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]


def item_order_totals(company_name: str = None):
    aggregator = []

    if company_name is not None:
        aggregator.append({
            '$match': {
                'FACTORY': company_name
            }
        })

    aggregator = aggregator + [{
        '$group': {
            '_id': {
                'FACTORY': '$FACTORY',
                'STATE': '$STATE',
                'ITEM': '$ITEM.NAME'
            },
            'REVENUE': {
                '$sum': {
                    '$toDouble': '$ITEM.PRICE'
                }
            },
            'QUANTITY_SOLD': {
                '$sum': '$ITEM.QUANTITY'
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'FACTORY': '$_id.FACTORY',
            'STATE': '$_id.STATE',
            'ITEM': '$_id.ITEM',
            'REVENUE': 1,
            'QUANTITY_SOLD': 1
        }
    }]

    return aggregator
