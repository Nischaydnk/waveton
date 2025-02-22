import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Image Annotation'

# Link to repo. Report bugs/features here :)
repo_url = 'https://github.com/vopani/waveton'
issue_url = f'{repo_url}/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D'

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
meta = ui.meta_card(
    box='',
    title='WaveTon',
    layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone(name='header'),
                ui.zone(
                    name='main',
                    size='calc(100vh - 150px)',
                    direction='row',
                    zones=[
                        ui.zone(name='image_entities', size='20%'),
                        ui.zone(name='image_annotator', size='70%'),
                        # ui.zone(name='save_annotations',size='20%',direction='column')
                    ]
                ),
                ui.zone(name='footer',),
                # ui.zone(name='main',direction='row',zones = ui.zone(name='save_annotations')),

            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Image Annotation ',
    subtitle='Annotate Images with Bounding Boxes Object Detection tasks',
    icon='Handwriting',
    icon_color='black',
    items=[
        ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)
    ]
)

# The footer shown on all the app's pages
footer = ui.footer_card(
    box='footer',
    caption=f'Learn more about <a href="{repo_url}" target="_blank"> WaveTon: 💯 Wave Applications</a>'
)

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)


def image_entities(image_tags: list[dict]) -> ui.FormCard:
    """
    Card for Image entities.
    """

    card = ui.form_card(
        box='image_entities',
        items=[
            ui.textbox(name='add_new_class', label='Add New Class'),
            ui.buttons(
                items=[
                    ui.button(name='add', label='Add', primary=True)
                ],
                justify='center'
            ),
            ui.separator(),
            ui.dropdown(
                name='delete_existing_class',
                label='Delete Existing Class',
                choices=[ui.choice(name=tag['name'], label=tag['label']) for tag in image_tags]
            ),
            ui.buttons(
                items=[
                    ui.button(name='delete', label='Delete', primary=True)
                ],
                justify='center'
            ),

            ui.separator(),

            ui.textbox(name='new_pixel_size', label='New Image Size [Integer]', suffix='px'),
            ui.buttons(
                items=[
                    ui.button(name='change_pixel', label='Change Size', primary=True)
                ],
                justify='center'
            ),

            ui.file_upload(name='file_upload', label='Click to Upload Custom Image!!', multiple=True,
                           file_extensions=['png', 'jpg']),

        ]
    )

    return card



def image_annotator(
    image_tags: list[dict],
    images: list,
    image_items: list,
    image_pixels: str,
) -> ui.FormCard:
    """
    Card for IMAGE annotator.
    """

    card = ui.form_card(
        box='image_annotator',

        items=[
            ui.image_annotator(
                name='annotator',
                title='Drag to annotate',
                image=[images][0],
                items=[image_items][0],
                image_height=image_pixels,
                tags= [ui.image_annotator_tag(**tag) for tag in image_tags],
            ),

            ui.buttons(
                items=[
                    ui.button(name='save_output', label='Download Output CSV File', primary=True,),
                ]
            ),
            # ui.textbox(name='textbox_suffix', label='Enter Filename to Save', suffix='.json'),

        ]
    )

    return card



def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content): return '\n'.join(['```', *content, '```'])

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)

    dump = [
        '### Stack Trace',
        code_block(stack_trace),
    ]

    states = [
        ('q.app', q.app),
        ('q.user', q.user),
        ('q.client', q.client),
        ('q.events', q.events),
        ('q.args', q.args)
    ]
    for name, source in states:
        dump.append(f'### {name}')
        dump.append(code_block([f'{k}: {v}' for k, v in expando_to_dict(source).items()]))

    return ui.form_card(
        box='main',
        items=[
            ui.stats(
                items=[
                    ui.stat(
                        label='',
                        value='Oops!',
                        caption='Something went wrong',
                        icon='Error'
                    )
                ],
            ),
            ui.separator(),
            ui.text_l(content='Apologies for the inconvenience!'),
            ui.buttons(items=[ui.button(name='reload', label='Reload', primary=True)]),
            ui.expander(name='report', label='Error Details', items=[
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content=f'Report Issue in App: **{app_name}**'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )
