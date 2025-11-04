import { useMemo } from "react";

export function useSortUsers(filteredData: { id: number; name: string; email: string; role: string; status: string; joinDate: string; }[], sortColumn: string, sortDirection: string) {
  return useMemo(() => {
    return [...filteredData].sort((a, b) => {
      //1.get the values to compare a[sortColumn] and b[sortColumn]
      //2.compare them (handle strings vs numbers)
      //3.multiply by -1 if sort direction === 'desc'
      const firstValue = a[sortColumn];
      const secondValue = b[sortColumn];

      let comparison = 0;
      if (typeof firstValue === "string" && typeof secondValue === "string") {
        comparison = firstValue.localeCompare(secondValue);
      } else if (typeof firstValue === "number" &&
        typeof secondValue === "number") {
        comparison = firstValue - secondValue;
      } else {
        // fallback
        if (firstValue > secondValue) comparison = 1;
        else if (secondValue < firstValue) comparison = -1;
      }

      // direction control
      return sortDirection === "asc" ? comparison : -comparison;
    });
  }, [filteredData, sortColumn, sortDirection]);
}

