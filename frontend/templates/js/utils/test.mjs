import { assert } from '/js/libs/chai.mjs';

export function hasFlags(output, expectedFlags){
	const expectedFlagsSet = new Set(expectedFlags);
	const sameFlags = (expectedFlagsSet.size === output.flags.size) && [...output.flags].every(flag => expectedFlagsSet.has(flag));
	return assert(sameFlags, `Expected flags ${[...expectedFlagsSet]}, got ${[...output.flags]}`);
};

export function hasFlag(output, flag){
	return () => assert(output.flags.has(flag), `Output has no "${flag}" flag. Flags are: ${[...output.flags].join(', ')}`);
};

export function notHasFlag(output, flag){
	return () => assert(!output.flags.has(flag), `Output has unexpected "${flag}" flag`);
};

export function yearsAgo(yearCount){
	return ((date) => date.setFullYear(date.getFullYear() - yearCount) && date)(new Date())
}