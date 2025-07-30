import time, sys, os

try:
	from . import __init__ as ims
	from . import units as u
except ImportError:
	sys.path.insert(1, '../')
	import hb9imsutils as ims
	import hb9imsutils.units as u

DELAY = "7m3"

u.VERBOSE = "-d" in sys.argv


@ims.PTimer
def high_accuracy_sleep(duration):
	end = duration + time.perf_counter()
	while time.perf_counter() < end:
		pass


def _test_number_converter(string):
	converted = u.number_converter(string)
	print(f"{string} -> {u.unitprint(converted) if converted is not None else converted} ({converted})")


@ims.timed
def test(x, y, z, w, v, u):
	# number_converter test
	delay = u.number_converter(DELAY)
	# unitprint tests
	print(f"Delay in loop set to {delay} ({u.unitprint(delay, 's')})")
	print()
	print("UNITPRINT TESTS")
	print()
	print(x)
	print(u.unitprint(x, "m"))
	print(u.unitprint(x, "m", power=1))
	print(u.unitprint(x, "m", power=2))
	print(u.unitprint(x, "m", power=3))

	print()
	print("UNITPRINT2 TESTS")
	print()
	print(w)
	print(u.unitprint2(w, "B"))  # normal test
	print(u.unitprint2(w * 1024, "B"))  # one more test
	print(u.unitprint2(w * 1024 ** 10, "B"))  # too many test
	print()


	# number_converter tests
	print("+ NUMBER_CONVERTER TESTS")
	_test_number_converter("5k6")
	_test_number_converter("5.6k")
	_test_number_converter("5ex6")
	_test_number_converter("5.6ex")
	_test_number_converter("56e8")
	_test_number_converter("5.6e9")
	_test_number_converter(".56e10")
	print()
	print("- NUMBER_CONVERTER TESTS")
	_test_number_converter("5.6ex9")
	_test_number_converter("5.6.e9")
	_test_number_converter(".5.6e9")
	_test_number_converter("5.6e")
	_test_number_converter("5.6f9")
	print()

	# progres_bar tests

	t_s = time.time()
	for i in range(y):
		print(ims.progress_bar(i, y, time.time() - t_s), end="")
		time.sleep(delay)
	print(ims.progress_bar(y, y, time.time() - t_s))

	t_s = time.time()
	for i in range(y):
		print(ims.progress_bar(i, z, time.time() - t_s), end="")
		time.sleep(delay)
	print(ims.progress_bar(y, z, time.time() - t_s))
	print()

	# ProgressBar tests

	for i in ims.ProgressBar(range(y), y):
		time.sleep(delay)

	for i in ims.ProgressBar(range(y), z):
		time.sleep(delay)
	print()

	pb = ims.ProgressBar(None, y)
	for i in range(y):
		time.sleep(delay)
		pb()
	print()

	pb = ims.ProgressBar(None, z)
	for i in range(y):
		time.sleep(delay)
		pb()
	print()
	print()

	# PTimer Test
	for _ in range(v):
		high_accuracy_sleep(u)
	print(high_accuracy_sleep.summary_long())
	timed_sleep = ims.PTimer(time.sleep, print_rate=100, length="long")
	for _ in range(v):
		timed_sleep(u)
	print(timed_sleep.summary_long())


def main():
	test(1e-18, 200, 100, 3**42, 1000, 0.001)
	time.sleep(5)


if __name__ == '__main__':
	main()
