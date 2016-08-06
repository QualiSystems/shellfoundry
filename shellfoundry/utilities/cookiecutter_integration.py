from cookiecutter.main import cookiecutter
import os


class CookiecutterTemplateCompiler:
    def __init__(self):
        pass

    def compile_template(self, shell_name, template_path, extra_context, running_on_same_folder):

        extra_context['project_name'] = shell_name
        if running_on_same_folder:
            output_dir = os.path.pardir
        else:
            output_dir = os.path.curdir

        cookiecutter(template_path, no_input=True,
                     extra_context=extra_context,
                     overwrite_if_exists=False, output_dir=output_dir)
