import copy
import re
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Literal, Optional, get_args

from box import Box
from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from ..book.item import Priority, Status, TodoItem
from ..book.result import (
    ActionResult,
    AddResult,
    EditResult,
    HistoryResult,
    QueryResult,
    SwitchResult,
    ViewResult,
)
from ..book.select import GroupBy
from ..common import has_prefix, json_dumps
from .common import pluralize, shorten, strip_rich, timedelta_format

RenderStats = Literal[True, False, "all"]


class Renderer:
    def __init__(self, config: Box, idempotent: bool = False):
        super().__init__()
        self.config = config
        self.idempotent = idempotent

    def _get_stats(
        self,
        count_todos: List[TodoItem],
        all_todos: Optional[List[TodoItem]] = None,
    ) -> Dict[str, int | float]:
        stats = {}
        for status in get_args(Status):
            if status == "delete":
                continue
            stats[status] = len([t for t in count_todos if t.status == status])
            if all_todos is not None:
                len_all = len([t for t in all_todos if t.status == status])
                stats[status + "_hidden"] = len_all - stats[status]
        if all_todos is not None:
            stats["hidden"] = len(all_todos) - len(count_todos)
        done = stats["done"]
        total = done + stats["pending"]
        stats["progress_filtered"] = done / total if total > 0 else None
        if all_todos is not None:
            done += stats["done_hidden"]
            total += stats["done_hidden"] + stats["pending_hidden"]
            stats["progress_all"] = done / total if total > 0 else None
        return stats

    def _render_by_format_map(
        self,
        todo: Optional[TodoItem],
        format_map: str | Dict[str, str],
        text_to_render: str,
        early_exit: bool = False,
        match_func: Optional[Callable[[Any, Any], bool]] = None,
    ) -> str:
        if isinstance(format_map, str):
            return format_map.format(text_to_render)
        rendered = format_map.get("_", "{}").format(text_to_render)
        if todo is None:
            return rendered
        for k, v in format_map.items():
            if ":" not in k:
                continue
            p, q = k.split(":")
            a = getattr(todo, p)
            if match_func is not None:
                match = match_func(q, a)
            elif isinstance(a, list):
                match = q in a
            else:
                match = q == a
            if not match:
                continue
            rendered = v.format(rendered)
            if early_exit:
                return rendered
        return rendered

    def _render_id(self, todo: Optional[TodoItem], id: int) -> Optional[str]:
        if self.idempotent:
            return f"{id} {self.config.token.separator}"
        return self._render_by_format_map(
            todo, self.config.item.id.format, str(id)
        )

    def _render_status(
        self,
        todo: Optional[TodoItem],
        status: Status,
    ) -> Optional[str]:
        if todo is None:
            return self.config.group.header.status[status]
        if self.idempotent:
            return f"{self.config.token.status}{status}"
        return self._render_by_format_map(
            todo, self.config.item.status.format, status
        )

    def _render_title(
        self, todo: Optional[TodoItem], title: str
    ) -> Optional[str]:
        if self.idempotent:
            tokens = "".join(rf"\b(\{v})" for v in self.config.token.values())
            title = re.sub(tokens, r"\1", title)
            return title
        else:
            for token in self.config.token.values():
                title = title.replace(f"\\{token}", token)
        style = self.config.item.title
        title = shorten(title, style.max_length, style.ellipsis)
        return self._render_by_format_map(todo, style.format, title)

    def _render_tags(
        self, todo: Optional[TodoItem], tags: List[str]
    ) -> Optional[str]:
        new_tags = []
        tag_formats = self.config.item.tag.format
        for tag in tags:
            if self.idempotent:
                tag = "+" + tag
            if tag in tag_formats:
                text = tag_formats[tag]
            else:
                text = self._render_by_format_map(todo, tag_formats, tag)
            new_tags.append(text)
        return " ".join([tag for tag in new_tags])

    def _render_project(
        self, todo: Optional[TodoItem], project: str
    ) -> Optional[str]:
        token = self.config.token.project
        return self._render_by_format_map(
            todo,
            self.config.item.project.format,
            project,
            match_func=lambda q, a: has_prefix(a.split(token), q.split(token)),
        )

    def _render_priority(
        self, todo: Optional[TodoItem], priority: Priority
    ) -> Optional[str]:
        if todo is None:
            return self.config.group.header.priority[priority]
        if self.idempotent:
            return f"{self.config.token.priority}{priority}"
        return self._render_by_format_map(
            todo, self.config.item.priority.format, priority
        )

    def _render_parent(
        self, todo: Optional[TodoItem], parent: Optional[int]
    ) -> Optional[str]:
        if parent is None:
            return None
        if self.idempotent:
            return f"{self.config.token.parent}{parent}"
        return self._render_by_format_map(
            todo, self.config.item.parent.format, str(parent)
        )

    def _render_deadline(
        self,
        deadline: Optional[date | datetime],
        status: Status,
        header: bool = False,
    ) -> Optional[str]:
        prefix = self.config.token.deadline
        deadline_format = self.config.item.deadline.format
        if deadline is None:
            if not header:
                return None
            return deadline_format["_"].format(f"{prefix}oo")
        if deadline == "overdue":
            return deadline_format[0].format(f"{prefix}{deadline}")
        if deadline == "today":
            return deadline_format[86400].format(f"{prefix}{deadline}")
        if isinstance(deadline, str):
            return f"{prefix}{deadline}"
        d = deadline.date() if isinstance(deadline, datetime) else deadline
        if (datetime.now().date() - d).days / 365 > 1000:
            return deadline_format[0].format(f"{prefix}-oo")
        if type(deadline) is date:
            deadline = datetime.combine(deadline, datetime.max.time())
        if self.idempotent:
            return f'{prefix}{deadline:"%Y-%b-%d %H:%M"}'
        remaining_time = deadline - datetime.now()
        seconds = abs(remaining_time.total_seconds())
        if abs(seconds) < 365 * 24 * 60 * 60:  # one year
            if header:
                format = self.config.group.header.deadline
            else:
                format = self.config.item.deadline
            text = prefix + timedelta_format(
                remaining_time, format.timedelta, format.num_components
            )
        else:
            dt_fmt = self.config.item.deadline.datetime
            text = f"{prefix}{deadline:{dt_fmt}}"
        rich_format = self.config.item.deadline.format
        if status in ["done", "note"]:
            fmt = rich_format.status_done
        else:
            fmt = rich_format._
            for k, v in rich_format.items():
                if isinstance(k, int) and remaining_time.total_seconds() < k:
                    fmt = v
        return fmt.format(text)

    def _render_created_at(self, created_at: datetime) -> Optional[str]:
        return self.config.item.created_at.format.format(created_at)

    def _render_description(
        self, todo: Optional[TodoItem], description: Optional[str]
    ) -> Optional[str]:
        if description is None:
            return None
        if self.idempotent:
            return f"{self.config.token.description} {description}"
        style = self.config.item.description
        desc = shorten(description, style.max_length, style.ellipsis)
        return self._render_by_format_map(
            todo, self.config.item.description.format, desc
        )

    def _render_header(self, group_by: GroupBy, value: Any) -> str | None:
        if group_by == "id":
            return None
        if group_by == "project":
            return self._render_project(None, value)
        if group_by == "tag":
            return self._render_tags(None, [value])
        if group_by == "priority":
            return self._render_priority(None, value)
        if group_by == "status":
            return self._render_status(None, value)
        if group_by == "parent":
            return self._render_parent(None, value)
        if group_by == "deadline":
            return self._render_deadline(value, "pending", True)
        if group_by == "created_at":
            return self._render_created_at(value)
        raise ValueError(f"Unknown group_by: {group_by}")

    def _render_fields(self, todo: TodoItem) -> Dict[str, str]:
        fields = {
            "id": self._render_id(todo, todo.id),
            "status": self._render_status(todo, todo.status),
            "title": self._render_title(todo, todo.title),
            "tags": self._render_tags(todo, todo.tags),
            "priority": self._render_priority(todo, todo.priority),
            "project": self._render_project(todo, todo.project),
            "parent": self._render_parent(todo, todo.parent),
            "deadline": self._render_deadline(todo.deadline, todo.status),
            "description": self._render_description(todo, todo.description),
        }
        return {k: " " + v if v else "" for k, v in fields.items()}

    def render_item(self, todo: TodoItem, group_by: GroupBy = "id") -> str:
        fields = self._render_fields(todo)
        format = self.config.group.format[group_by]
        return format.format(**fields)[1:]

    def render_item_diff(
        self, before_todo: TodoItem, after_todo: TodoItem
    ) -> str:
        def strip_color(fields):
            return {k: strip_rich(v) for k, v in fields.items()}

        before_nc = strip_color(self._render_fields(before_todo))
        after = self._render_fields(after_todo)
        after_nc = strip_color(after)
        fields = {}
        diff_format = self.config.item.diff.format
        for k, v in before_nc.items():
            if v == after_nc[k]:
                fields[k] = after[k]
            else:
                bv, av = before_nc[k].lstrip(), after[k].lstrip()
                fields[k] = " " + diff_format.format(bv, av)
        return self.config.item.format.format(**fields)[1:]

    def render_stats(
        self,
        filtered_todos: List[TodoItem],
        all_todos: List[TodoItem],
    ) -> str:
        separator = self.config.stats.separator
        stats = self._get_stats(filtered_todos, all_todos)
        progress_text = []
        for key in ("filtered", "all"):
            progress = stats["progress_" + key]
            if progress is None:
                continue
            if key == "filtered" and len(filtered_todos) == len(all_todos):
                continue
            progress_str = f"{stats['progress_' + key]:.0%}"
            progress_map = self.config.stats.progress
            progress_format = progress_map._
            for k, v in progress_map.items():
                if isinstance(k, int) and progress * 100 <= k:
                    progress_format = v
            progress_str = progress_format.format(progress_str)
            stats_format = self.config.stats.title[key]
            progress_text.append(stats_format.format(progress_str))
        text = []
        if progress_text:
            text.append(separator.join(progress_text))
        stats_text = []
        formats = self.config.stats.status
        for key in get_args(Status):
            if key == "delete":
                continue
            count = stats[key]
            hidden = stats.get(key + "_hidden", 0)
            if hidden > 0:
                value = formats[key + "_hidden"].format(count, hidden)
                stats_text.append(value)
            else:
                stats_text.append(formats[key].format(count))
        text.append(separator.join(stats_text))
        return "\n".join(text)

    def render(
        self,
        grouped_todos: Dict[Any, List[TodoItem]],
        group_by: GroupBy,
        idempotent: Optional[bool] = None,
    ) -> str:
        old_idempotent = self.idempotent
        if idempotent is not None:
            self.idempotent = idempotent
        text = []
        if not grouped_todos:
            return self.config.message.empty
        for group, gtodos in grouped_todos.items():
            if not gtodos:
                continue
            if group_by != "id":
                stats = self._get_stats(gtodos)
                progress = f"[{stats['done']}/{len(gtodos)}]"
                group = self._render_header(group_by, group)
                header = self.config.group.header.format.format(
                    group=group, progress=progress
                )
                text.append(header)
            for todo in gtodos:
                item = f"{self.render_item(todo, group_by)}"
                text.append(item)
            text.append("")
        text = text[:-1]  # remove last empty line
        if idempotent is not None:
            self.idempotent = old_idempotent
        return "\n".join(text)

    def render_result(
        self, result: ActionResult
    ) -> RenderableType | List[RenderableType]:
        try:
            render_func = getattr(self, f"render_{type(result).__name__}")
        except AttributeError:
            raise ValueError(f"Unknown result type: {type(result)}")
        return render_func(result)

    def render_ViewResult(self, result: ViewResult) -> str:
        return self.render(result.grouped_todos, result.group_by)

    def render_QueryResult(self, result: QueryResult) -> str:
        values = []
        for row in result.values:
            row = [v.isoformat() if isinstance(v, datetime) else v for v in row]
            row = row[0] if len(row) == 1 else row
            value = row if isinstance(row, int | str) else json_dumps(row)
            values.append(value)
        return "\n".join(values)

    def render_AddResult(self, result: AddResult) -> str:
        items = [self.render_item(item) for item in result.items]
        count = len(result.items)
        message = self.config.message.add.format(
            count, pluralize("item", count)
        )
        return "\n".join([message, ""] + items)

    def render_EditResult(self, result: EditResult) -> str:
        if not result.after:
            text = [self.config.message.no_edit]
        else:
            c = len(result.after)
            message = self.config.message.edit.format(c, pluralize("item", c))
            text = [message]
            text.append("")
        for btodo, atodo in zip(result.before, result.after):
            text.append(self.render_item_diff(btodo, atodo))
        return "\n".join(text)

    def render_HistoryResult(self, result: HistoryResult) -> RenderableType:
        history_config = self.config.view.history
        max_length = history_config.max_length
        timedelta = history_config.timedelta
        num_components = history_config.num_components
        table = Table(box=box.ROUNDED)
        table.add_column("Time", justify="right")
        table.add_column("Commit")
        for item in result.history[:max_length]:
            dt = datetime.now() - item.timestamp.replace(tzinfo=None)
            dt = timedelta_format(dt, timedelta, num_components)
            table.add_row(dt, item.message)
        return table

    def render_SwitchResult(self, result: SwitchResult) -> List[RenderableType]:
        format = getattr(self.config.message, result.action)
        text = format.format(result.message)
        panels = []
        for ar in result.action_results:
            if isinstance(ar, AddResult) and result.action == "undo":
                after = copy.deepcopy(ar.items)
                for a in after:
                    a.status = "delete"
                diffs = [
                    self.render_item_diff(b, a) for b, a in zip(ar.items, after)
                ]
                count = len(ar.items)
                message = self.config.message.undo_add.format(
                    count, pluralize("item", count)
                )
                panels.append([message, ""] + diffs)
            if isinstance(ar, AddResult) and result.action == "redo":
                items = [self.render_item(a) for a in ar.items]
                message = self.config.message.redo_add.format(
                    len(ar.items), pluralize("item", len(ar.items))
                )
                panels.append([message, ""] + items)
            if isinstance(ar, EditResult):
                message = self.config.message.undo_edit.format(
                    len(ar.after), pluralize("item", len(ar.after))
                )
                panel = [message, ""]
                for btodo, atodo in zip(ar.before, ar.after):
                    if result.action == "undo":
                        btodo, atodo = atodo, btodo
                    panel.append(self.render_item_diff(btodo, atodo))
                panels.append(panel)
        panels = [
            Panel(Group(*panel), expand=False) for panel in panels if panel
        ]
        return [text] + panels
