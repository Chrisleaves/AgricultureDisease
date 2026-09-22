param(
  [string]$OutputDirectory = (Join-Path $PSScriptRoot "..\src\static\tabbar")
)

Add-Type -AssemblyName System.Drawing

$size = 81
$inactive = [System.Drawing.ColorTranslator]::FromHtml("#647067")
$active = [System.Drawing.ColorTranslator]::FromHtml("#287b4d")

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

function New-IconCanvas([System.Drawing.Color]$color) {
  $bitmap = New-Object System.Drawing.Bitmap($size, $size)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.Clear([System.Drawing.Color]::Transparent)
  $pen = New-Object System.Drawing.Pen($color, 4)
  $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
  $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
  return @($bitmap, $graphics, $pen)
}

function Save-Icon($canvas, [string]$name) {
  $bitmap, $graphics, $pen = $canvas
  $bitmap.Save((Join-Path $OutputDirectory $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $pen.Dispose()
  $graphics.Dispose()
  $bitmap.Dispose()
}

function New-DiagnosisIcon([System.Drawing.Color]$color, [string]$name) {
  $canvas = New-IconCanvas $color
  $bitmap, $graphics, $pen = $canvas
  $graphics.DrawLine($pen, 24, 15, 24, 32)
  $graphics.DrawLine($pen, 42, 15, 42, 32)
  $graphics.DrawArc($pen, 24, 24, 18, 27, 0, 180)
  $graphics.DrawLine($pen, 33, 51, 33, 57)
  $graphics.DrawArc($pen, 33, 43, 27, 24, 90, -180)
  $graphics.DrawEllipse($pen, 56, 33, 11, 11)
  Save-Icon $canvas $name
}

function New-RecordIcon([System.Drawing.Color]$color, [string]$name) {
  $canvas = New-IconCanvas $color
  $bitmap, $graphics, $pen = $canvas
  $graphics.DrawRectangle($pen, 18, 13, 39, 53)
  $graphics.DrawLine($pen, 27, 26, 47, 26)
  $graphics.DrawLine($pen, 27, 36, 45, 36)
  $graphics.DrawLine($pen, 27, 46, 39, 46)
  $graphics.DrawLine($pen, 42, 59, 65, 36)
  $graphics.DrawLine($pen, 60, 34, 67, 41)
  $graphics.DrawLine($pen, 42, 59, 40, 67)
  Save-Icon $canvas $name
}

function New-GuideIcon([System.Drawing.Color]$color, [string]$name) {
  $canvas = New-IconCanvas $color
  $bitmap, $graphics, $pen = $canvas
  $points = [System.Drawing.Point[]]@(
    [System.Drawing.Point]::new(12, 20), [System.Drawing.Point]::new(31, 13),
    [System.Drawing.Point]::new(50, 20), [System.Drawing.Point]::new(69, 13),
    [System.Drawing.Point]::new(69, 59), [System.Drawing.Point]::new(50, 66),
    [System.Drawing.Point]::new(31, 59), [System.Drawing.Point]::new(12, 66)
  )
  $graphics.DrawPolygon($pen, $points)
  $graphics.DrawLine($pen, 31, 14, 31, 59)
  $graphics.DrawLine($pen, 50, 20, 50, 65)
  Save-Icon $canvas $name
}

New-DiagnosisIcon $inactive "diagnosis.png"
New-DiagnosisIcon $active "diagnosis-active.png"
New-RecordIcon $inactive "record.png"
New-RecordIcon $active "record-active.png"
New-GuideIcon $inactive "guide.png"
New-GuideIcon $active "guide-active.png"
