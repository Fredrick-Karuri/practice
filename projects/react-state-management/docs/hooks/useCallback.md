useCallback is about preserving referential equality(the concept where two variables or values are considered equal
if they point to the same object in memory, rather than simply having the same value) so that optimization tools like 
React.memo can work properly.

Both useCallback and useMemo preserve references when dependencies are unchanged
useMemo has two costs: 
 .running the dependency check every render
 .storing the momoized value in memory
for sth like todos.filter which is :
    .fast to compute(just looping and checking a boolean)
    .small result(just a filtered array)
the overhead of useMemo might actually be slower that just running the filter.