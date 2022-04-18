run: stats.py lint
	./$<
lint: stats.py
	pylint3 $<
