import questionary
import subprocess
import os
import platform

def run_command(command):
    if platform.system() == "Windows":
        if command[0] in {"npx", "npm", "nuxi"}:
            command[0] += ".cmd"
        subprocess.run(command, shell=True)
    else:
        subprocess.run(command)

def handle_react():
    frontend_lang = questionary.select(
        "Choose language for React:",
        choices=["JavaScript", "TypeScript"]
    ).ask()

    cra_version = questionary.text("Enter CRA version (leave blank for latest):").ask()

    if frontend_lang == "TypeScript":
        if not cra_version:
            run_command(["npx", "create-react-app", ".", "--template", "typescript"])
        else:
            run_command(["npx", f"create-react-app@{cra_version}", ".", "--template", "typescript"])
    else:
        if not cra_version:
            run_command(["npx", "create-react-app", "."])
        else:
            run_command(["npx", f"create-react-app@{cra_version}", "."])

# def handle_next():
#     next_lang = questionary.select(
#         "Choose language for Next.js:", 
#         choices=["JavaScript", "TypeScript"]
#         ).ask()
    
#     version = questionary.text("Enter the version you want to install(leave for the latest)").ask()

#     if next_lang == "JavaScript":
#         if not version:
#             run_command(["npx", "create-next-app", "."])

# def handle_frontend():
#     frontend_choice = questionary.select(
#         "Select Frontend Technology:",
#         choices=["React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "SolidJS", "Qwik", "Astro"]
#     ).ask()
    

#     frontend_lang = None
#     if frontend_choice == "React":
#         handle_react()
#     #     frontend_lang = questionary.select(
#     #         "Choose language for React:",
#     #         choices=["JavaScript", "TypeScript"]
#     #     ).ask()

#     # print("\nCreating frontend...")

#     # if frontend_choice == "React":
#     #     if frontend_lang == "JavaScript":
#     #         run_command(["npx", "create-react-app", ".", "--template", "javascript"])
#     #     else:
#     #         run_command(["npx", "create-react-app", ".", "--template", "typescript"])
#     elif frontend_choice == "Next.js":
#         next_lang = questionary.select(
#             "Choose language for Next.js:",
#             choices=["JavaScript", "TypeScript"]
#         ).ask()

#         if next_lang == "TypeScript":
#             run_command(["npx", "create-next-app", ".", "--typescript"])
#         else:
#             run_command(["npx", "create-next-app", "."])
#     elif frontend_choice == "Vue":
#         run_command(["npm", "init", "vue@latest"])
#     elif frontend_choice == "Angular":
#         run_command(["npx", "@angular/cli", "new", os.getcwd()])
#     elif frontend_choice == "Svelte":
#         run_command(["npm", "create", "vite@latest", ".", "--", "--template", "svelte"])
#     elif frontend_choice == "Nuxt.js":
#         run_command(["npx", "nuxi", "init", "."])
#     elif frontend_choice == "SolidJS":
#         run_command(["npm", "create", "solid@latest"])
#     elif frontend_choice == "Qwik":
#         run_command(["npm", "create", "qwik@latest"])
#     elif frontend_choice == "Astro":
#         run_command(["npm", "create", "astro@latest"])

def handle_frontend():
    frontend_choice = questionary.select(
        "Select Frontend Technology:",
        choices=["React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "SolidJS", "Qwik", "Astro"]
    ).ask()

    if frontend_choice == "React":
        handle_react()

    elif frontend_choice == "Next.js":
        next_lang = questionary.select(
            "Choose language for Next.js:",
            choices=["JavaScript", "TypeScript"]
        ).ask()
        version = questionary.text("Enter Next.js version (leave blank for latest):").ask()

        base_cmd = ["npx", f"create-next-app{('@' + version) if version else ''}", "."]
        if next_lang == "TypeScript":
            base_cmd.append("--typescript")
        run_command(base_cmd)

    elif frontend_choice == "Vue":
        version = questionary.text("Enter Vue CLI version (leave blank for latest):").ask()
        if version:
            run_command(["npm", "init", f"vue@{version}"])
        else:
            run_command(["npm", "init", "vue@latest"])

    elif frontend_choice == "Angular":
        version = questionary.text("Enter Angular CLI version (leave blank for latest):").ask()
        dir_name = os.path.basename(os.getcwd())
        if version:
            run_command(["npx", f"@angular/cli@{version}", "new", dir_name])
        else:
            run_command(["npx", "@angular/cli", "new", dir_name])

    elif frontend_choice == "Svelte":
        version = questionary.text("Enter Vite version for Svelte (leave blank for latest):").ask()
        if version:
            run_command(["npm", "create", f"vite@{version}", ".", "--", "--template", "svelte"])
        else:
            run_command(["npm", "create", "vite@latest", ".", "--", "--template", "svelte"])

    elif frontend_choice == "Nuxt.js":
        version = questionary.text("Enter Nuxt version (leave blank for latest):").ask()
        if version:
            run_command(["npx", f"nuxi@{version}", "init", "."])
        else:
            run_command(["npx", "nuxi", "init", "."])

    elif frontend_choice == "SolidJS":
        version = questionary.text("Enter SolidJS version (leave blank for latest):").ask()
        if version:
            run_command(["npm", "create", f"solid@{version}"])
        else:
            run_command(["npm", "create", "solid@latest"])

    elif frontend_choice == "Qwik":
        version = questionary.text("Enter Qwik version (leave blank for latest):").ask()
        if version:
            run_command(["npm", "create", f"qwik@{version}"])
        else:
            run_command(["npm", "create", "qwik@latest"])

    elif frontend_choice == "Astro":
        version = questionary.text("Enter Astro version (leave blank for latest):").ask()
        if version:
            run_command(["npm", "create", f"astro@{version}"])
        else:
            run_command(["npm", "create", "astro@latest"])
