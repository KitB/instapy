# Instapy -- Interactive Python
## Libraries
Most of the requirements are in `requirements.txt` so you can create a
virtualenv with:

~~~~{.bash}
virtualenv --system-site-packages instapy.site.env
source instapy.site.env/bin/activate
pip install -r requirements.txt
~~~~

Note that you need to enable `system-site-packages` because the project also
requires `pygame` which does not currently compile using `pip` so you will need
to acquire it by other means.

Once you have the requirements installed (and ensuring you have the virtualenv
enabled -- the `source ...` line in the above script does this) you can run
`python run.py examples/objects/interactive.Game` to try out the interactive
example. You will also need to run `python run_gui.py` to initiate automatic
updating (the main process just exposes a server). With these running, open
`examples/objects/interactive.py` and try changing things (note that the
`init_once` method is explicitly unmodifiable, so don't worry if you make
changes in that and it doesn't work).

Bigass caveat: Behaviour on threads is undefined and will definitely do wrong
things. Don't use this on threads.
