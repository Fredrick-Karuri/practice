"""
# The big questions for every design:
1.What data needs to be stored
2.How will it be queried (read heavy vs write heavy)
3.What relatioships exist?
4.What needs to be fast?

## Key concepts cheatsheet
# Relationships
1.One to Many: User -> Posts (one user many posts)
2.Many to Many: Students <-> Courses (needs a junction table)
3.One to One: User -> UserProfile (rare, usually just combine tables)

# Normalization vs Denormalization
1.Normalized: No duplicate data, multiple joins needed
    .Pro:Easy to update, no inconsistencies
    .Con:Slower reads(more joins)

2.Denormalized:Duplicate data for speed
    .Pro:Faster reads(fewer joins)
    .Con:Harder to update consistently

# Indexes
.Speed up reads on specific columns
.Slow down writes(index must be updated)
.Rule:Index columns you filter/sort by frequently

# Transactions
.Multiple operations that must ALL succeed or ALL fail
.Example: Transfer money(deduct from A, add to B - both or neither)





"""