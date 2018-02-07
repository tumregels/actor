import logging
import os
import os.path as op
import sys
from subprocess import Popen, PIPE

script = """\
on launch_actor(actor_path)
	tell application "System Events"
		-- Don't create multiple windows if Terminal is not running
		-- For some reason this sometimes throws an error on SnowLeopard
		try
			set terminal_count to count (processes whose bundle identifier is "com.apple.Terminal")
		on error
			set terminal_count to 1
		end try
		if terminal_count is 0 then
			tell application "Terminal"
				activate
				try
					do script ("exec '" & actor_path & "'") in window 0
				on error
					-- If there's no window 0, just have it do it
					do script ("exec '" & actor_path & "'")
				end try
			end tell
		else
			-- Terminal was already running, open a new window
			tell application "Terminal"
				do script ("exec '" & actor_path & "'")
				activate
			end tell
		end if
	end tell
end launch_actor

launch_actor("{}")
"""

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
    cwd = op.dirname(sys.executable)
else:
    # we are running in a normal Python environment
    bundle_dir = op.join(op.dirname(op.abspath(__file__)), op.pardir)
    cwd = bundle_dir

os.chdir(cwd)

logging.basicConfig(
    filename=op.join(cwd, 'log.txt'),
    filemode='w',
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# uncomment this line to print logs in console
# logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)


def run_osascript():
    args = []
    p = Popen(['/usr/bin/osascript', '-'] + args,
              stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    actor_path = op.abspath(op.join(cwd, op.pardir, 'Resources', 'actor'))

    logger.info(actor_path)
    stdout, stderr = p.communicate(script.format(actor_path))

    logger.info(stdout)
    logger.error(stderr)

    p.wait()


if __name__ == '__main__':
    run_osascript()
