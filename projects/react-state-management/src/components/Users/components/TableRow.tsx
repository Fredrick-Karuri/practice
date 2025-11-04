import React from "react";

  export const TableRow = React.memo( ({user}) =>(
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
  ));