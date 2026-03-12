The `frontend/js` directory contains plain Javascript modules.

- `constants.mjs.jinja` is a way to pass Python variables to Javascript when generating the website.
- `components` contains plain Javascript components that do not require VueJS
- `utils` contains plain Javascript utility functions
- `vue` contains Vue-specific code
    - `vue/tools` contains complete, embeddable components (calculators, letter generators etc.). Those can be included in the content with the `{% tool %}` tag. For example `{% tool "health-insurance-calculator", static=True %}`
    - `vue/components` contains building blocks that are used to make tools.
    - `vue/mixins` contains Vue mixins.