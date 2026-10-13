const CLASS = {
  "To Do": "badge badge-todo",
  "In Progress": "badge badge-progress",
  "In Review": "badge badge-review",
  Done: "badge badge-done",
};

export default function StatusBadge({ value }) {
  return <span className={CLASS[value] || "badge"}>{value}</span>;
}
