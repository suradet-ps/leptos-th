# การปรับปรุงประสบการณ์การพัฒนาด้วย Leptos (Leptos DX)

มีเครื่องมือและเทคนิคหลายอย่างที่ช่วยให้ประสบการณ์การพัฒนาเว็บและแอปด้วย Leptos สะดวกสบายยิ่งขึ้นอย่างเห็นได้ชัด การสละเวลาสักครู่เพื่อตั้งค่าสภาพแวดล้อมการทำงานตามคำแนะนำในบทนี้ จะช่วยให้คุณเขียนโค้ดได้อย่างมีประสิทธิภาพ รวดเร็ว และลดความหงุดหงิดลงไปได้มาก โดยเฉพาะอย่างยิ่งหากคุณต้องการเขียนโค้ดตามตัวอย่างในหนังสือเล่มนี้

## 1) ตั้งค่า `console_error_panic_hook`

ตามค่าเริ่มต้น หากโค้ด WebAssembly ของคุณเกิดข้อผิดพลาดรุนแรง (panic) ขณะรันบนเบราว์เซอร์ สิ่งที่คุณเห็นในคอนโซลของเบราว์เซอร์จะมีเพียงข้อความ error สั้นๆ ที่ไม่ช่วยอะไรมากนัก เช่น `Unreachable executed` พร้อมสแตกเทรซ (stack trace) ที่ชี้ไปยังตำแหน่งในไบนารี WASM

การติดตั้ง `console_error_panic_hook` จะเปลี่ยนข้อความเหล่านั้นให้กลายเป็นสแตกเทรซของ Rust ที่ระบุชื่อไฟล์และบรรทัดในซอร์สโค้ด Rust ของคุณโดยตรง

วิธีตั้งค่าง่ายมาก:

1. รันคำสั่ง `cargo add console_error_panic_hook` ในโปรเจกต์ของคุณ
2. ในฟังก์ชัน `main` ให้เพิ่มโค้ด `console_error_panic_hook::set_once();`

> หากต้องการดูตัวอย่างจริง [คลิกที่นี่เพื่อดูตัวอย่างโค้ด](https://github.com/leptos-rs/leptos/blob/main/examples/counter/src/main.rs#L6)

เพียงเท่านี้ เมื่อเกิด panic บนเบราว์เซอร์ คุณก็จะได้ข้อความแจ้งเตือนที่เข้าใจง่ายและช่วยดีบักได้อย่างรวดเร็ว!

## 2) ระบบช่วยเติมโค้ด (Autocompletion) สำหรับ `#[component]` และ `#[server]`

ด้วยธรรมชาติของมาโครใน Rust (ที่สามารถแปลงโค้ดจากรูปแบบหนึ่งไปเป็นอีกรูปแบบหนึ่งได้หลากหลาย แต่จะทำงานได้ก็ต่อเมื่อโค้ดที่ป้อนเข้ามาถูกต้องสมบูรณ์ 100% ณ เสี้ยววินาทีนั้น) จึงทำให้เครื่องมืออย่าง rust-analyzer ประสบปัญหาในการทำงานร่วมกับมาโคร และอาจทำให้ฟีเจอร์อย่าง autocompletion หรือการตรวจสอบโค้ดทำงานผิดพลาดหรือไม่แสดงผล

หากคุณพบปัญหาระบบช่วยพิมพ์ไม่ทำงานหรือ IDE แจ้ง error แปลกๆ เมื่อใช้มาโครเหล่านี้ คุณสามารถตั้งค่าให้ rust-analyzer ข้ามการประมวลผลโพรซีเดอรัลมาโคร (procedural macros) บางตัวได้ โดยเฉพาะอย่างยิ่งกับมาโคร `#[server]` ซึ่งทำหน้าที่เพียงแอนโนเทตฟังก์ชัน แต่ไม่ได้แปลงโค้ดภายในเนื้อฟังก์ชัน การปิดการประมวลผลมาโครนี้จะช่วยให้ระบบช่วยเติมโค้ดทำงานได้อย่างราบรื่นมาก

```admonish note 
ตั้งแต่ Leptos เวอร์ชัน 0.5.3 เป็นต้นมา rust-analyzer ได้รับการปรับปรุงให้รองรับมาโคร `#[component]` ได้ดีขึ้นมาก แต่หากคุณยังพบปัญหาอยู่ คุณสามารถเพิ่ม `#[component]` เข้าไปในรายการ macro ignore ได้เช่นกัน (ดูตัวอย่างด้านล่าง)
โปรดทราบว่าการข้ามการประมวลผล `#[component]` จะทำให้ rust-analyzer ไม่รู้จักพร็อพ (props) ของคอมโพเนนต์ ซึ่งอาจทำให้ IDE แสดงคำเตือนหรือข้อผิดพลาดเกี่ยวกับพร็อพขึ้นมาแทน
```

สำหรับ **VSCode** ในไฟล์ `settings.json`:

```json
"rust-analyzer.procMacro.ignored": {
	"leptos_macro": [
        // optional:
		// "component",
		"server"
	],
}
```

สำหรับ **VSCode** เมื่อใช้งานร่วมกับ `cargo-leptos` ใน `settings.json`:
```json
"rust-analyzer.procMacro.ignored": {
	"leptos_macro": [
        // optional:
		// "component",
		"server"
	],
},
// if code that is cfg-gated for the `ssr` feature is shown as inactive,
// you may want to tell rust-analyzer to enable the `ssr` feature by default
//
// you can also use `rust-analyzer.cargo.allFeatures` to enable all features
"rust-analyzer.cargo.features": ["ssr"]
```

สำหรับ **Neovim**:

```lua
vim.lsp.config('rust_analyzer', {
  -- Other Configs ...
  settings = {
    ["rust-analyzer"] = {
      -- Other Settings ...
      procMacro = {
        ignored = {
          leptos_macro = {
            -- optional: --
            -- "component",
            "server",
          },
        },
      },
    },
  }
})
```

สำหรับ **Helix** ใน `.helix/languages.toml`:

```toml
[[language]]
name = "rust"

[language-server.rust-analyzer]
config = { procMacro = { ignored = { leptos_macro = [
	# Optional:
	# "component",
	"server"
] } } }
```

สำหรับ **Zed** ใน `settings.json`:

```json
{
  -- Other Settings ...
  "lsp": {
    "rust-analyzer": {
      "initialization_options": {
        "procMacro": {
          "ignored": {
            "leptos_macro": [
				// Optional:
				// "component",
				"server"
			],
          },
        },
      },
    },
  },
}
```

สำหรับ **SublimeText 3** เมนู `Goto Anything...` เลือกไฟล์ `LSP-rust-analyzer.sublime-settings`:

```json
// Settings in here override those in "LSP-rust-analyzer/LSP-rust-analyzer.sublime-settings"
{
  "rust-analyzer.procMacro.ignored": {
    "leptos_macro": [
      // optional:
      // "component",
      "server"
    ],
  },
}
```
## 3) เปิดใช้งาน Cargo Features ใน Rust-Analyzer (ไม่บังคับ)

ตามค่าเริ่มต้น rust-analyzer จะวิเคราะห์โค้ดโดยอิงจาก default features ของโปรเจกต์เท่านั้น แต่ Leptos ใช้ feature flags หลายตัวในการควบคุมการคอมไพล์ เช่น ในโปรเจกต์ CSR เราใช้ฟีเจอร์ `csr` ในจุดต่างๆ ส่วนในโปรเจกต์ SSR เราจะใช้ `ssr` สำหรับโค้ดฝั่งเซิร์ฟเวอร์ และ `hydrate` สำหรับโค้ดที่จะนำไปรันบนเบราว์เซอร์

วิธีการเปิดใช้งานฟีเจอร์เหล่านี้ขึ้นอยู่กับแต่ละ IDE เราได้รวบรวมการตั้งค่ายอดนิยมไว้ด้านล่างนี้ หากไม่มี IDE ที่คุณใช้ ให้มองหาการตั้งค่าชื่อ `rust-analyzer.cargo.features` หรือ `rust-analyzer.cargo.allFeatures`

สำหรับ **VSCode** ใน `settings.json`:
```json
{
  "rust-analyzer.cargo.features": "all",  // Enable all features
}
```

สำหรับ **Neovim** ใน `init.lua`:
```lua
vim.lsp.config('rust_analyzer', {
  settings = {
    ["rust-analyzer"] = {
      cargo = {
        features = "all", -- Enable all features
      },
    },
  }
})

```
สำหรับ **Helix** ใน `.helix/languages.toml` หรือเฉพาะโปรเจกต์ใน `.helix/config.toml`:
```toml
[[language]]
name = "rust"

[language-server.rust-analyzer.config.cargo]
allFeatures = true
```

สำหรับ **Zed** ใน `settings.json`:

```json
{
  -- Other Settings ...
  "lsp": {
    "rust-analyzer": {
      "initialization_options": {
        "cargo": {
          "allFeatures": true // Enable all features
        }
      }
	}
  }
}
```

สำหรับ **SublimeText 3** ในการตั้งค่าผู้ใช้ของ `LSP-rust-analyzer-settings.json`:
```json
 {
        "settings": {
            "LSP": {
                "rust-analyzer": {
                    "settings": {
                        "cargo": {
                            "features": "all"
                        }
                    }
                }
            }
        }
    }
```


## 4) ติดตั้งและใช้งาน `leptosfmt` (ไม่บังคับ)

`leptosfmt` เป็นเครื่องมือจัดรูปแบบโค้ด (code formatter) ที่สร้างขึ้นมาโดยเฉพาะสำหรับมาโคร `view!` ของ Leptos (ซึ่งเป็นจุดที่คุณเขียนโค้ดสร้าง UI) เนื่องจากมาโคร `view!` รองรับไวยากรณ์สไตล์ 'RSX' (ซึ่งคล้ายกับ JSX ในฝั่ง React) เครื่องมือมาตรฐานอย่าง `cargo-fmt` จึงไม่สามารถจัดรูปแบบโค้ดภายในมาโครได้อย่างสวยงาม ครีต `leptosfmt` จึงเข้ามาช่วยแก้ปัญหานี้ เพื่อให้โค้ด UI ของคุณอ่านง่าย สวยงาม และเป็นระเบียบเรียบร้อยอยู่เสมอ

คุณสามารถติดตั้งและเรียกใช้งาน `leptosfmt` ผ่านบรรทัดคำสั่งหรือตั้งค่าให้ทำงานร่วมกับเอดิเตอร์ได้ดังนี้:

เริ่มแรก ให้ติดตั้งเครื่องมือผ่าน Cargo:

`cargo install leptosfmt`

หากต้องการจัดรูปแบบโค้ดจากบรรทัดคำสั่งด้วยการตั้งค่าเริ่มต้น ให้รันคำสั่ง `leptosfmt ./**/*.rs` จากรากของโปรเจกต์

### การสั่งให้รันอัตโนมัติใน IDE ที่รองรับ Rust Analyzer

หากคุณต้องการตั้งค่าให้เอดิเตอร์เรียกใช้ `leptosfmt` อัตโนมัติทุกครั้งที่บันทึกไฟล์ หรือต้องการปรับแต่งการทำงาน สามารถศึกษาขั้นตอนอย่างละเอียดได้ที่[หน้า README.md ของรีโพ `leptosfmt` บน GitHub](https://github.com/bram209/leptosfmt)

> **ข้อแนะนำ**: เพื่อผลลัพธ์ที่ดีที่สุด แนะนำให้กำหนดการตั้งค่า `leptosfmt` แบบเจาะจงรายเวิร์กสเปซ (per-workspace)

### การสั่งให้รันอัตโนมัติใน RustRover

เนื่องจาก RustRover ยังไม่รองรับ Rust Analyzer จึงต้องใช้วิธีอื่นในการสั่งรัน `leptosfmt` โดยอัตโนมัติ แนวทางหนึ่งคือการติดตั้งปลั๊กอิน [FileWatchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) แล้วกำหนดค่าดังนี้:

- Name: Leptosfmt
- File type: Rust files
- Program: `/path/to/leptosfmt` (หรือใส่เพียง `leptosfmt` หากตัวโปรแกรมอยู่ในพาธ `$PATH` ของระบบแล้ว)
- Arguments: `$FilePath$`
- Output paths to refresh: `$FilePath$`


## 5) ใช้ `--cfg=erase_components` ระหว่างการพัฒนา

ในเวอร์ชัน Leptos 0.7 มีการปรับปรุงตัวเรนเดอร์หลายจุดโดยพึ่งพาระบบ Type System ของ Rust อย่างเข้มข้นยิ่งขึ้น ซึ่งในโปรเจกต์ขนาดใหญ่อาจส่งผลให้เวลาคอมไพล์ช้าลง ปัญหานี้สามารถแก้ไขได้เกือบทั้งหมดด้วยการเปิดใช้งานคอมไพเลอร์แฟล็กพิเศษ `--cfg=erase_components` ในระหว่างขั้นตอนการพัฒนา (แฟล็กนี้จะช่วยลบข้อมูลชนิดข้อมูลบางส่วนออก เพื่อลดภาระการทำงานของคอมไพเลอร์และลดขนาดของ debug info ที่สร้างขึ้น โดยแลกมาด้วยขนาดไบนารีที่ใหญ่ขึ้นเล็กน้อยและ overhead ขณะรันไทม์ จึงแนะนำให้ใช้เฉพาะในโหมด dev เท่านั้น และไม่ควรใช้ในโหมด release)

ตั้งแต่ `cargo-leptos` เวอร์ชัน v0.2.40 เป็นต้นมา ระบบจะเปิดใช้งานแฟล็กนี้ให้คุณโดยอัตโนมัติเมื่ออยู่ในโหมดพัฒนา แต่หากคุณใช้งาน Trunk หรือไม่ได้ใช้ `cargo-leptos` หรือต้องการเปิดใช้งานด้วยตนเอง คุณสามารถส่งแฟล็กผ่านบรรทัดคำสั่งได้อย่างง่ายดาย (`RUSTFLAGS="--cfg erase_components" trunk serve` หรือ `RUSTFLAGS="--cfg erase_components" cargo leptos watch`) หรือจะกำหนดไว้ล่วงหน้าในไฟล์ `.cargo/config.toml` ของคุณก็ได้:

```toml
# use your own native target
[target.aarch64-apple-darwin]
rustflags = [
  "--cfg",
  "erase_components",
]

[target.wasm32-unknown-unknown]
rustflags = [
   "--cfg",
   "erase_components",
]
```
