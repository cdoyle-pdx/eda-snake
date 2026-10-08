# eda-snake

EDA Snake as an installable Nokia EDA application,100% vibe-coded over the
course of a few days using Claude Opus 4.5 (medium). I have Claude Pro and
was able to build this without exceeding any included limits. The process
started with the idea and progressed through game development, testing,
EDA integration, and EDA catalog repo creation. When encountered, errors
were pasted back into the chat for diagnosis.

### THE POINT IS THIS -> Anyone with an idea, regardless of their coding experience, can convert an idea into an EDA application.

Development used the 'edabuilder' **25.8** app development workflow. It has
been tested using version 26.8.1 of the EDA Playground and eda-telemetry lab.
I can't promise it will work on older versions because I haven't tried.

The game launches from the "Snake" app category in the EDA UI, opening a 
new browser tab. The leaderboard exists as a series of custom resources in
the EDB. Default launch settings and leaderboard namespace configuration is
available within the Snake application category.

---

## App integration summary

EDA has two classes of app: intent apps written in MicroPython, and
**controller-based apps** which can be written in any language. Snake is both:

| Part | Class | Why |
|---|---|---|
| `SnakeScore`, `SnakeLeaderboard` CRDs | API resources | Leaderboard state lives in the EDB, so it is transactional, git-backed and revertible |
| `intents/snakeleaderboard/state_intent.py` | State intent | Ranks scores server-side and raises the new-high-score alarm |
| `k8s/deployment.yaml` + `service.yaml` | Controller-based | The game is a browser UI, so it needs something serving it |

No **config** intent exists, deliberately: Snake does not generate device
configuration, so there is nothing for a config script to push. That said,
if a fabric isn't detected, the game will still play in a standalone mode.

## Installing EDA-Snake

1. Configure my EDA app catalog (https://github.com/cdoyle-pdx/eda-catalog) on
your EDA cluster. Be sure to note the Public Key requirement!
2. Install the "Snake" application from the EDA Cluster app store.
3. Locate the "Snake" application category in the Main menu and expand.
4. Click on the "Snake Config" app and click the 'Create' button.
5. (optional) The critical setting here is the namespace for the leaderboard. The
application default is the "eda" namespace. Modify as-required. Other
settings can be left alone if you like, and the Name (required) has
no functional significance (so call it whatever you like).
6. Click the "Play Snake" app and click the 'View" link in the
small Snake dashboard element to launch the game.

## Known issues and considerations

- The game launches as a proxy using the cluster UI IP. I used the default
port 9443 defined in the prefs.mk file. If you have configured a differet
port, things might not work. I've not tested it to find out.
- If you are trying to play the game from the local host, the game will
not function as intended if you actually use 'localhost' in your address.
Changing to the public IP or '127.0.0.1' sorts things out.
- The Fabric integration expects version 6.0.0 of the Fabrics application. It
will complain if you try to install the EDA-Snake app on an EDA cluster
running an older version (like v5.0.0).
