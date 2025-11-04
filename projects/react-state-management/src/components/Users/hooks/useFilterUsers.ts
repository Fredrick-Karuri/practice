import { useMemo } from "react";
import {USERS} from '../UserDataTable'

export function useFilterUsers(debouncedSearch: string, roleFilter: string) {
  return useMemo(() => {
    return USERS.filter((user) => {
      const matchesSearchTerm = user.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        user.email.toLowerCase().includes(debouncedSearch.toLowerCase());
      const matchesRole = roleFilter === "all" || user.role === roleFilter;
      return matchesSearchTerm && matchesRole;
    });
  }, [debouncedSearch, roleFilter]);
}