from distutils.core import setup
import py2exe

setup(
	name="Spotify Watcher",
	version="1.0.0",
	author="Michael Eaton",
	author_email="byzanitnefailure@gmail.com",
	description="Writes the current spotify song to ./spotify.txt",
	#long_description=open("README.md").read(),
	console=["spotify_watcher.py"],
	zipfile=None,
	options={
		'py2exe':{
			'bundle_files': 0,
			'xref': False,
			'optimize': 2,
			'compressed': 1
		}
	}
)
