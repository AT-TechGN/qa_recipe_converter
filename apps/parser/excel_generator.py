import io
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.filters import AutoFilter


# Color palette
COLOR_HEADER_BG = "1E3A5F"       # Deep navy
COLOR_HEADER_FG = "FFFFFF"       # White
COLOR_ALT_ROW = "F0F4FA"         # Light blue-gray
COLOR_AUTOMATED_BG = "E8F5E9"    # Light green
COLOR_BORDER = "B0BEC5"          # Light gray border
COLOR_TITLE_BG = "2D6A9F"        # Medium blue for "Cas automatisé" header


COLUMNS = [
    ('use_case_id', 'Use Case', 18),
    ('description', 'Description', 40),
    ('preconditions', 'Préconditions', 35),
    ('steps', 'Étapes', 45),
    ('expected_results', 'Résultats Attendus', 40),
    ('observed_results', 'Résultats Observés', 40),
    ('status', 'Statut', 15),
]


def make_border(color=COLOR_BORDER):
    side = Side(style='thin', color=color)
    return Border(left=side, right=side, top=side, bottom=side)


def make_header_fill(color=COLOR_HEADER_BG):
    return PatternFill(start_color=color, end_color=color, fill_type='solid')


def make_alt_fill():
    return PatternFill(start_color=COLOR_ALT_ROW, end_color=COLOR_ALT_ROW, fill_type='solid')


def make_automated_fill():
    return PatternFill(
        start_color=COLOR_AUTOMATED_BG,
        end_color=COLOR_AUTOMATED_BG,
        fill_type='solid'
    )


class ExcelGenerator:
    def __init__(self, use_cases, source_filename: str = ''):
        self.use_cases = list(use_cases)
        self.source_filename = source_filename
        self.wb = Workbook()

    def generate(self) -> io.BytesIO:
        """Generate Excel workbook and return as BytesIO buffer."""
        self._build_use_cases_sheet()
        self._build_automated_sheet()

        # Remove default sheet if it exists
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        buffer = io.BytesIO()
        self.wb.save(buffer)
        buffer.seek(0)
        return buffer

    def _build_use_cases_sheet(self):
        ws = self.wb.create_sheet("Use Cases")
        self._write_sheet(ws, self.use_cases, header_color=COLOR_HEADER_BG)

    def _build_automated_sheet(self):
        automated_ucs = [uc for uc in self.use_cases if uc.is_automated]
        ws = self.wb.create_sheet("Cas automatisé")
        self._write_sheet(ws, automated_ucs, header_color=COLOR_TITLE_BG)

    def _write_sheet(self, ws, use_cases, header_color: str):
        """Write use cases to a worksheet with professional formatting."""
        # --- Title row ---
        ws.append([f"Fichier source : {self.source_filename}"])
        title_cell = ws.cell(row=1, column=1)
        title_cell.font = Font(bold=True, size=11, color="444444")
        title_cell.alignment = Alignment(horizontal='left')
        ws.row_dimensions[1].height = 20

        # Merge title across all columns
        num_cols = len(COLUMNS) + 1  # +1 for row number
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)

        # --- Header row (row 2) ---
        header_row = ['N°'] + [col[1] for col in COLUMNS]
        ws.append(header_row)
        header_fill = make_header_fill(header_color)
        header_font = Font(bold=True, color=COLOR_HEADER_FG, size=10)
        border = make_border()

        for col_idx, cell in enumerate(ws[2]):
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(
                horizontal='center',
                vertical='center',
                wrap_text=True
            )
            cell.border = border

        ws.row_dimensions[2].height = 30

        # Set column widths
        ws.column_dimensions['A'].width = 6  # N° column
        for i, (_, _, width) in enumerate(COLUMNS):
            col_letter = get_column_letter(i + 2)
            ws.column_dimensions[col_letter].width = width

        # Freeze panes (freeze header)
        ws.freeze_panes = 'A3'

        # --- Data rows ---
        alt_fill = make_alt_fill()
        auto_fill = make_automated_fill()

        for row_num, uc in enumerate(use_cases, start=1):
            row_data = [row_num]
            for field_name, _, _ in COLUMNS:
                if field_name == 'status':
                    row_data.append(uc.status)
                else:
                    row_data.append(getattr(uc, field_name, ''))

            ws.append(row_data)
            excel_row = row_num + 2  # offset for title + header rows

            # Apply fill: green for automated, alternating gray for others
            if uc.is_automated:
                fill = auto_fill
            elif row_num % 2 == 0:
                fill = alt_fill
            else:
                fill = None

            for col_idx in range(1, len(row_data) + 1):
                cell = ws.cell(row=excel_row, column=col_idx)
                if fill:
                    cell.fill = fill
                cell.border = border
                cell.alignment = Alignment(
                    vertical='top',
                    wrap_text=True,
                    horizontal='left' if col_idx > 1 else 'center'
                )
                if col_idx == 1:
                    cell.font = Font(bold=True, size=10)
                else:
                    cell.font = Font(size=10)

            ws.row_dimensions[excel_row].height = 60

        # --- Auto-filter on header row ---
        if use_cases:
            last_col = get_column_letter(len(COLUMNS) + 1)
            ws.auto_filter.ref = f"A2:{last_col}{len(use_cases) + 2}"

        # Summary at bottom
        if use_cases:
            summary_row = len(use_cases) + 4
            ws.cell(row=summary_row, column=1, value=f"Total : {len(use_cases)} cas de tests")
            ws.cell(row=summary_row, column=1).font = Font(bold=True, italic=True, color="666666")
