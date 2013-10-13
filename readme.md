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
`python run.py examples/no_objects/interactive.Game` to try out the interactive
example. With this running, open `examples/no_objects/interactive.py` and try
changing things (note that the `init_once` method is explicitly unmodifiable, so
don't worry if you make changes in that and it doesn't work).
