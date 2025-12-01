import readline
import inspect
import shlex
import re

class Shell:
    def __init__(self,
                 motd: str ="Welcome to PyShell! Type 'help' for available commands, and 'exit' to quit.",
                 prompt: str =">>> ",
                 help_command: str ="help",
                 exit_command: str ="exit",
                 set_command: str = "set",
                 exit_dialog: str ="Exiting PyShell...",
                 unknown_cmd_dialog: str ="Unknown command."):
        self.COMMANDS = {}
        self.variables = {}
        self.motd = motd
        self.prompt = prompt
        self.help_command = help_command
        self.exit_command = exit_command
        self.set_command = set_command
        self.exit_dialog = exit_dialog
        self.unknown_cmd_dialog = unknown_cmd_dialog

        self.COMMANDS[self.set_command] = self._set_var

    def expand_vars(self, text: str) -> str:
        def repl(match):
            name = match.group(1)
            return self.variables.get(name, f"${name}")
        return re.sub(r"\$(\w+)", repl, text)

    def _set_var(self, name: str, value: str):
        self.variables[name] = value
        return f"{name} = {value}"

    def command(self, *, aliases: list =None):
        if aliases is None:
            aliases = []

        def decorator(func):
            self.COMMANDS[func.__name__] = func
            for alias in aliases:
                self.COMMANDS[alias] = func
            return func

        return decorator

    def run(self):
        print(self.motd)
        while True:
            try:
                user_input = input(self.prompt).strip()
                if user_input == self.exit_command:
                    print(self.exit_dialog)
                    break
                if not user_input:
                    continue
                self.execute_line(user_input)
            except KeyboardInterrupt:
                print(f"\nTo exit the program, run '{self.exit_command}'.")
            except Exception as e:
                print(f"Error: {e}")
    
    def execute_line(self, user_input: str):
        user_input = self.expand_vars(user_input)

        input_parts = [part.strip() for part in user_input.split("|")]
        commands = [shlex.split(part) for part in input_parts]
        input_data = None
    
        for parts in commands:
            if not parts:
                continue
            cmd_name, *arg_strings = parts
            if cmd_name == self.help_command:
                print("Available commands:\n -", "\n - ".join(self.COMMANDS.keys()))
                break
            if cmd_name not in self.COMMANDS:
                print(self.unknown_cmd_dialog)
                break
    
            func = self.COMMANDS[cmd_name]
            sig = inspect.signature(func)
            kwargs = {}
            pos_args = []
            i = 0
            while i < len(arg_strings):
                if arg_strings[i].startswith("--"):
                    key = arg_strings[i][2:]
                    i += 1
                    if i < len(arg_strings):
                        kwargs[key] = arg_strings[i]
                    else:
                        raise ValueError(f"Flag '--{key}' requires a value")
                else:
                    pos_args.append(arg_strings[i])
                i += 1
            if input_data is not None:
                pos_args.insert(0, input_data)
            bound_args = sig.bind_partial(*pos_args, **kwargs)
            bound_args.apply_defaults()
            for name, value in bound_args.arguments.items():
                param = sig.parameters[name]
                if param.annotation is not inspect._empty and not isinstance(value, param.annotation):
                    bound_args.arguments[name] = param.annotation(value)
            result = func(*bound_args.args, **bound_args.kwargs)
            input_data = result
        if input_data is not None:
            print(input_data)

    def run_script(self, filepath: str):
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    print(f"{self.prompt}{line}")
                    self.execute_line(line)
        except FileNotFoundError:
            print(f"Script file not found: {filepath}")
        except Exception as e:
            print(f"Error running script: {e}")



