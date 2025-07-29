import argparse
import streamlit as st
import shlex
from copy import deepcopy
from streamlit_tags import st_tags

class Form():
    def __init__(
        self,
        parser,
        **kwargs
    ):
        self.parser = deepcopy(parser)
        # Ensure we continue in case of errors
        self.parser.exit = lambda *args, **kwargs: None
        self.parser.error = lambda *args, **kwargs: None

        # A few hacks to get the raw input for each action
        def get_value(action, arg_string, dummy=None):
            return arg_string

        raw_parser = deepcopy(self.parser)

        raw_parser._get_value = get_value
        raw_parser._check_value = get_value

        for action in raw_parser._actions:
            action.default = None
            action.required = False

        self.raw_parser = raw_parser
        self.widget_map = kwargs

    def render(self, args):
        # Now we can get the raw inputs for each option string
        result = self.raw_parser.parse_args(args)
        parser = self.parser

        new_result = {}
        for action in parser._actions:
            # Skip supressed actions
            if not hasattr(result, action.dest):
                continue

            # Use the original parser to 
            # get the supplied values and cast them
            # to the correct type for the program's
            # vocabulary.
            value = getattr(result, action.dest)
            match value:
                case None:
                    pass
                case [*_]:
                    value = [str(v) for v in value]
                    value = parser._get_values(
                        action, value
                    )
                case _:
                    value = [str(value)]
                    value = parser._get_values(
                        action, value
                    )

            # Use it to initialize the widget
            st.session_state[action.dest] = st.session_state.get(
                action.dest,
                value
            )
            # Get new values for the widgets. The returned value will
            # be in the user's vocabulary, not the program's vocabulary.

            # If we have an override for this field, we call it now
            if action.dest in self.widget_map:
                value = self.widget_map[action.dest](self, action, value)
                new_result[action.dest] = value
            # Else we generate widgets for each action
            # TODO: this does not work if we have both a type and
            # choices.
            else:
                match action:
                    case argparse._HelpAction():
                        continue
                    case argparse.Action(choices=[*choices], nargs=None):
                        new_result[action.dest] = st.selectbox(
                            label=action.dest,
                            help=action.help,
                            key=action.dest,
                            index=None,
                            options=choices
                        )
                    case argparse.Action(nargs="+", choices=[*choices]):
                        indices = st.multiselect(
                            label=action.dest,
                            help=action.help,
                            options=choices
                        )
                        new_result[action.dest] = indices
                    case argparse.Action(nargs="*", choices=[*choices]):
                        indices = st.multiselect(
                            label=action.dest,
                            help=action.help,
                            options=choices
                        )
                        new_result[action.dest] = indices
                    case argparse.Action(nargs='+'):
                        new_result[action.dest] = st_tags(
                            label=action.dest,
                            value=getattr(result, action.dest)
                        )
                    case argparse.Action(nargs='*'):
                        new_result[action.dest] = st_tags(
                            label=action.dest,
                            value=getattr(result, action.dest)
                        )
                    case argparse.Action():
                        new_result[action.dest] = st.text_input(
                            label=action.dest,
                            value=getattr(result, action.dest)
                        )
                    case _:
                        continue

            # Now validate the input. We use the original parser
            # to do so.
            if new_result[action.dest]:
                value = new_result[action.dest]
                try:
                    if isinstance(value, list):
                        parser._get_values(action, value)
                    else:
                        parser._get_value(action, value)

                except Exception as e:
                    st.error(e)

            # Now validate required fields
            # FIXME: this should not be run before a submit
            if not new_result[action.dest] and action.required:
                st.error(f"{action.dest} is required")
                

        # Collect all results and make a new argparse string
        output = []
        for action in parser._actions:
            if action.dest not in new_result:
                continue
            if not new_result[action.dest]:
                continue
            match action:
                case argparse.Action(nargs=None):
                    output.append(f"--{action.dest}")
                    output.append(new_result[action.dest])
                case argparse.Action(nargs='?'):
                    if new_result[action.dest]:
                        output.append(f"--{action.dest}")
                        output.append(new_result[action.dest])
                case argparse.Action():
                    output.append(f"--{action.dest}")
                    output.extend(new_result[action.dest])

        output = [str(o) for o in output]

        parser.parse_args(output)
        return shlex.join(output)
