# directory synchronizer backup system
import sys
import main


Version = "0.0.0.0"



if len(sys.argv) < 2:
    print("Error: Action is not specified.\nUse help to list available actions.")
    exit(-1)

action = sys.argv[1]
args = main.ParseArgs(sys.argv[2:])

if action == "help":
    main.ShowHelp()
elif action == "index":
    main.Index(args)
elif action == "log":
    main.Log(args)
elif action == "status":
    main.Status(args)
elif action == "merge":
    main.Merge(args)
elif action == "push":
    main.Push(args)
elif action == "version":
    print(f"Version: {Version}")
elif action == "clean":
    main.Clean(args)
else:
    print(f"Error: Invalid action \"{action}\".\nUse help to list available actions.")
    exit(-1)

exit(0)