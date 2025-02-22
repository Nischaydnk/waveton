
import logging

from h2o_wave import Q, main, app, handle_on, on
import os

import cards
from style import load_model, stylize

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

models_choice = ['candy', 'mosaic', 'rain_princess', 'udnie','fire','black_rainbow','hex']
source_image_choice = ['house.jpg','beth.jpeg']
models_images = ['candy.jpg', 'mosaic.jpg', 'rain_princess.jpg', 'udnie.jpg','fire.jpg','black_rainbow.jpg','hex.jpg']


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    print(q.args)
    try:
        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)
            q.app.initialized = True  # Mark as initialized at the app level (global to all clients)

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await initialize_client(q)
            q.client.initialized = True  # Mark as initialized at the client (browser tab) level

        if q.args.source_img is not None:
            q.user.source_img = q.args.source_img
            img = q.args.source_img
            q.user.input_image = "static/" + img
            q.user.output_image = "static/" + img
            q.args.tabs = 'dashboard_tab'
        else:
            img = source_image_choice[0]
            q.user.input_image = "static/" + img
        
        if q.args.style_model is not None:
            q.user.style_model = q.args.style_model
            q.user.template_image_path, = await q.site.upload(['static/'+q.user.style_model+'.jpg'])
            q.args.tabs = 'dashboard_tab'
        
        if len(os.listdir('generated')) > 5:
            for i in os.listdir('generated'):
                os.remove('generated/'+i)


        if q.args.try_your_image:
            q.user.apply_style = False
            if q.user.try_your_image is True:
                q.user.try_your_image = False
            else:
                q.user.try_your_image = True
            q.args.tabs = 'dashboard_tab'

        
        if q.args.apply_style:
            if q.user.try_your_image is True:
                try:
                    local_path = await q.site.download(q.args.upload_image[0], 'input/'+q.args.upload_image[0].split('/')[-1].replace(' ','_'))
                    q.user.input_image = input_image = 'input/' + os.path.basename(local_path)
                    img = os.path.basename(local_path)
                except Exception as e:
                    print(e)
                    q.user.input_image = "static/" + img
            else:
                q.user.input_image = "static/" + img
            print(q.user.input_image)
            style_name = q.user.style_model
            print(style_name)
            model = "saved_models/" + style_name + ".pth"
            q.user.output_image = "generated/" + style_name + "-" + img
            model = load_model(model)     
            stylize(model, q.user.input_image, q.user.output_image)
            q.user.style_name = q.user.style_model
            q.user.apply_style = q.args.apply_style
            q.args.tabs = 'dashboard_tab'
        if q.user.apply_style:
            q.args.tabs = 'dashboard_tab'
            # Delegate query to query handlers
        if q.args.tabs == 'dashboard_tab':
            await dashboard_page(q, {})
        elif await handle_on(q):
            pass
        
        # This condition should never execute unless there is a bug in our code
        # Adding this condition here helps us identify those cases (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))

async def dashboard_page(q, details=None):
    cfg = await cards.create_dashboard(q,models_choice,source_image_choice)
    await cards.render_template(q, cfg)

async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info('Initializing app')

    # Add app-level initialization logic here (loading datasets, database connections, etc.)
    q.app.cards = ['main']


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')
    img = source_image_choice[0]
    q.user.input_image = "static/" + img
    q.user.style_model = 'candy'
    q.user.template_image_path, = await q.site.upload(['static/candy.jpg'])
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer
    await dashboard_page(q,{})


def clear_cards(q: Q, card_names: list):
    """
    Clear cards from the page.
    """

    logging.info('Clearing cards')

    for card_name in card_names:
        del q.page[card_name]


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    logging.error(error)

    # Clear all cards from the page
    clear_cards(q, q.app.cards)

    # Format and display the error
    q.page['error'] = cards.crash_report(q)

    await q.page.save()


@on('reload')
async def reload_client(q: Q):
    """
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """

    logging.info('Reloading client')

    # Reload the client
    await initialize_client(q)


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    This function should never get called unless there is a bug in our code or query handling logic.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()
