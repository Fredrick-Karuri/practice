import { useState } from "react";

const generateUsers = (count:number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role: ['Admin', 'User', 'Guest'][i % 3],
    status: ['Active', 'Inactive'][i % 2],
    joinDate: new Date(2020 + (i % 5), i % 12, (i % 28) + 1).toISOString()
  }));
};

const USERS = generateUsers(1000);

/*
what: data table with 1000 rows

requirements:
1.search by name
2.sort by any column
3.filter by role dropdown
4.pagination (50 per page)

states needed:
1.searchTerm
2.sortColumn
3.sortDirection
4.roleFilter
5.currentPage

functions to build:
1.filter logic
    -filter by search
    -filter by role
2.sorting logic
    -compare function based on sort column and sort direction
3.pagination logic (slice filterd array)
    -calculate `start index` and  `end_index` from currentPage
    -total pages = Math.ceil(filteredData.length/ITEMS_PER_PAGE)
4.Event handlers
    -handleSearch : update search term
    -handleSort : toggle direction if same column else reset to 'asc'
    -handleRoleFilter : update roleFilter, reset to page 1
    -handlePageChange : update current page

Processing order:
USERS -> filter by search -> filter by role -> sort -> paginate -> render
*/

export function UserDataTable (){
    const [searchTerm,setSearchTerm]= useState('')
    const [sortColumn,setSortColumn]= useState('id')
    const [sortDirection,setSortDirection] = useState('asc')
    const [roleFilter,setRoleFilter] = useState('all')
    const [currentPage,setCurrentPage]= useState(1)
    const ITEMS_PER_PAGE = 50

    // basic filtering:
    // todo:filter function that filters USERS by searchTerm (check name and email, case insensitive)
    // todo:add role filter to the same function

    const filteredData = USERS .filter(user=>{
        const matchesSearchTerm = user.name.toLowerCase().includes(searchTerm.toLowerCase()) || user.email.toLowerCase().includes(searchTerm.toLowerCase())
        const matchesRole = roleFilter === 'all' || user.role === roleFilter
        return matchesSearchTerm && matchesRole    
    })
    console.log("filtered data",filteredData)

    //sorting
    //todo: create a sort function that takes filtered data and returns sorted array based on sortColumn and sortDirection
    const sortedData=[...filteredData].sort((a,b)=>{
        //1.get the values to compare a[sortColumn] and b[sortColumn]
        //2.compare them (handle strings vs numbers)
        //3.multiply by -1 if sort direction === 'desc'

        const firstValue =a[sortColumn]
        const secondValue =b[sortColumn]

        let comparison = 0
        if (typeof firstValue === 'string' && typeof secondValue === 'string') {
            comparison=firstValue.localeCompare(secondValue)
        } else if (typeof firstValue === 'number' && typeof secondValue === 'number'){
            comparison= firstValue-secondValue
        } else {
            // fallback
            if (firstValue>secondValue) comparison = 1
            else if (secondValue<firstValue) comparison = -1
        }

        // direction control
        return sortDirection === 'asc' ? comparison : -comparison

    })
    console.log("sorted data count",sortedData.length)

    // pagination
    // 1.calculate pagination values (startIndex,endIndex,totalPages)
    // 2.slice sorted data to get current page items

    const totalPages = Math.ceil(sortedData.length/ITEMS_PER_PAGE)
    const startIndex = (currentPage-1) *ITEMS_PER_PAGE
    const endIndex =startIndex+ITEMS_PER_PAGE

    console.log(totalPages,startIndex,endIndex,currentPage)

    const paginatedData = sortedData.slice(startIndex,endIndex)
    // console.log("paginated data:",paginatedData)

    // handle search
    const handleSearch = (e) =>{
        setSearchTerm(e.target.value)
        setCurrentPage(1) //reset to page 1 when searching
    }
    const handleSort= (column)=>{
        if (sortColumn === column){
            // toggle direction if same column
            setSortDirection(sortDirection == 'asc'? 'desc':'asc')
        } else{
            //new column (reset to asc)
            setSortColumn(column)
            setSortDirection('asc')
        }
    }

    const handleRoleFilter = (role)=>{
        setRoleFilter(role)
        setCurrentPage(1) //rest to page 1 when filtering
    }

    const handlePageChange =(page)=>{
        setCurrentPage(page)
    }
return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
        {/* Search Input */}
        <div className="relative">
            <input 
                type="text" 
                value={searchTerm}
                placeholder="Search by name or email"
                onChange={handleSearch}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
        </div>

        {/* Role Filter */}
        <div className="flex flex-wrap gap-4 p-4 bg-gray-50 rounded-lg">
            <label className="flex items-center gap-2 cursor-pointer">
                <input 
                    type="radio" 
                    name="roleFilterGroup" 
                    checked={roleFilter === 'all'}
                    onChange={() => handleRoleFilter('all')}
                    className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">All Roles</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
                <input 
                    type="radio" 
                    name="roleFilterGroup" 
                    checked={roleFilter === 'Admin'}
                    onChange={() => handleRoleFilter('Admin')}
                    className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Admin</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
                <input 
                    type="radio" 
                    name="roleFilterGroup" 
                    checked={roleFilter === 'User'}
                    onChange={() => handleRoleFilter('User')}
                    className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">User</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
                <input 
                    type="radio" 
                    name="roleFilterGroup" 
                    checked={roleFilter === 'Guest'}
                    onChange={() => handleRoleFilter('Guest')}
                    className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Guest</span>
            </label>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th 
                            onClick={() => handleSort('name')}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        >
                            Name
                        </th>
                        <th 
                            onClick={() => handleSort('role')}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        >
                            Role
                        </th>
                        <th 
                            onClick={() => handleSort('id')}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        >
                            ID
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {paginatedData.map(user => (
                        <tr key={user.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {user.name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                {user.role}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {user.id}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between">
            <button 
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Previous
            </button>
            
            <span className="text-sm text-gray-700">
                Page {currentPage} of {totalPages}
            </span>
            
            <button 
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Next
            </button>
        </div>
    </div>
);

}