export const generateUsers = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role: ["Admin", "User", "Guest"][i % 3],
    status: ["Active", "Inactive"][i % 2],
    joinDate: new Date(2020 + (i % 5), i % 12, (i % 28) + 1).toISOString(),
  }));
};