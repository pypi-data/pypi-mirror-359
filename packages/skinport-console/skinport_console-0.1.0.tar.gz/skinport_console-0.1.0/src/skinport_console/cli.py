import asyncio

import inquirer
import skinport


async def cli():
    while True:
        endpoint = inquirer.list_input(
            'What do you want to do?',
            choices=[
                ('Get items', 0),
                ('Get sales history', 1),
                ('Get item out of stock', 2),
                ('Get account transactions', 3),
                ('Subscribe to sale feed', 4),
                ('Exit', 5)
            ])

        if endpoint == 0:
            items = await skinport.Client().get_items()

            text = inquirer.text(
                'Enter a search term (leave empty for all items)',
                default='',
            )

            market_hash_names = [(item.market_hash_name, item) for item in items if text.lower() in item.market_hash_name.lower()]

            if not market_hash_names:
                print('No items found.')
                continue

            item = inquirer.list_input(
                'Select an item to get details',
                choices=market_hash_names,
            )
            print(repr(item))

        elif endpoint == 1:
            items = await skinport.Client().get_sales_history()

            text = inquirer.text(
                'Enter a search term (leave empty for all items)',
                default='',
            )

            market_hash_names = [(item.market_hash_name, item) for item in items if text.lower() in item.market_hash_name.lower()]

            if not market_hash_names:
                print('No items found.')
                continue

            item = inquirer.list_input(
                'Select an item to get sales history',
                choices=market_hash_names,
            )
            print(repr(item))

        elif endpoint == 2:
            items = await skinport.Client().get_sales_out_of_stock()

            text = inquirer.text(
                'Enter a search term (leave empty for all items)',
                default='',
            )

            market_hash_names = [(item.market_hash_name, item) for item in items if text.lower() in item.market_hash_name.lower()]

            if not market_hash_names:
                print('No items found.')
                continue

            item = inquirer.list_input(
                'Select an item to get details',
                choices=market_hash_names,
            )
            print(repr(item))

        elif endpoint == 3:
            print('Not implemented')

        elif endpoint == 4:
            print('Not implemented')

        elif endpoint == 5:
            print('Exiting...')
            break


def main():
    asyncio.run(cli())
