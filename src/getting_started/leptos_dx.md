# การปรับปรุงประสบการณ์การพัฒนาด้วย Leptos

มีหลายสิ่งที่คุณทำได้เพื่อปรับปรุงประสบการณ์การพัฒนาเว็บไซต์และแอปด้วย Leptos คุณอาจอยากใช้เวลาสักสองสามนาทีตั้งค่าสภาพแวดล้อมของคุณเพื่อเพิ่มประสิทธิภาพในการพัฒนา โดยเฉพาะอย่างยิ่งหากคุณต้องการเขียนโค้ดตามตัวอย่างในหนังสือเล่มนี้

## 1) ตั้งค่า `console_error_panic_hook`

โดยค่าเริ่มต้น เมื่อโค้ด WASM ของคุณเกิด panic ขณะรันในเบราว์เซอร์ มันจะโยนข้อผิดพลาดในเบราว์เซอร์พร้อมข้อความที่ไม่ค่อยมีประโยชน์อย่าง `Unreachable executed` และสแตกเทรซที่ชี้เข้าไปในไบนารี WASM ของคุณ

เมื่อใช้ `console_error_panic_hook` คุณจะได้สแตกเทรซ Rust จริงที่ระบุบรรทัดในซอร์สโค้ด Rust ของคุณ

การตั้งค่านั้นง่ายมาก:

1. รัน `cargo add console_error_panic_hook` ในโปรเจกต์ของคุณ
2. ในฟังก์ชัน main ของคุณ เพิ่ม `console_error_panic_hook::set_once();`

> หากยังไม่ชัดเจน [คลิกที่นี่เพื่อดูตัวอย่าง](https://github.com/leptos-rs/leptos/blob/main/examples/counter/src/main.rs#L6)

ตอนนี้คุณควรได้ข้อความ panic ที่ดีขึ้นมากในคอนโซลของเบราว์เซอร์แล้ว!

## 2) การเติมโค้ดอัตโนมัติในเอดิเตอร์สำหรับ `#[component]` และ `#[server]`

เนื่องจากธรรมชาติของมาโคร (ซึ่งขยายจากอะไรก็ได้เป็นอะไรก็ได้ แต่ต้องมีอินพุตที่ถูกต้องเป๊ะในขณะนั้น) การที่ rust-analyzer จะเติมโค้ดอัตโนมัติและให้การสนับสนุนอื่นๆ อย่างถูกต้องจึงเป็นเรื่องยาก

หากคุณเจอปัญหาในการใช้มาโครเหล่านี้ในเอดิเตอร์ คุณสามารถบอก rust-analyzer ให้เพิกเฉยต่อโปรกมาโครบางตัวได้อย่างชัดเจน โดยเฉพาะอย่างยิ่งกับมาโคร `#[server]` ซึ่งใส่แอนโนเทชันให้เนื้อฟังก์ชันแต่ไม่ได้แปลงอะไรภายในเนื้อฟังก์ชันของคุณจริงๆ การทำเช่นนี้มีประโยชน์มาก

```admonish note 
 เริ่มตั้งแต่ Leptos เวอร์ชัน 0.5.3 ได้มีการเพิ่มการสนับสนุน rust-analyzer สำหรับมาโคร `#[component]` แต่หากคุณเจอปัญหา คุณอาจต้องการเพิ่ม `#[component]` เข้าไปในรายการมาโครที่เพิกเฉยด้วยเช่นกัน (ดูด้านล่าง)
โปรดทราบว่าการทำเช่นนี้หมายความว่า rust-analyzer จะไม่รู้จักพร็อพของคอมโพเนนต์ของคุณ ซึ่งอาจสร้างข้อผิดพลาดหรือคำเตือนชุดใหม่ใน IDE ได้
```

VSCode `settings.json`:

```json
"rust-analyzer.procMacro.ignored": {
	"leptos_macro": [
        // optional:
		// "component",
		"server"
	],
}
```

VSCode ร่วมกับ cargo-leptos `settings.json`:
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

Neovim:

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

Helix ใน `.helix/languages.toml`:

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

Zed ใน `settings.json`:

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

SublimeText 3 ภายใต้ `LSP-rust-analyzer.sublime-settings` ในเมนู `Goto Anything...`:

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
## 3) เปิดใช้งานฟีเจอร์ใน Rust-Analyzer สำหรับเอดิเตอร์ของคุณ (ไม่บังคับ)
โดยค่าเริ่มต้น rust-analyzer จะรันกับฟีเจอร์เริ่มต้นของโปรเจกต์ Rust ของคุณเท่านั้น Leptos ใช้ฟีเจอร์ที่แตกต่างกันเพื่อควบคุมการคอมไพล์ สำหรับโปรเจกต์ที่เรนเดอร์ฝั่งไคลเอนต์ เราใช้ `csr` ในหลายจุด ส่วนแอปที่เรนเดอร์ฝั่งเซิร์ฟเวอร์อาจมี `ssr` สำหรับโค้ดฝั่งเซิร์ฟเวอร์ และ `hydrate` สำหรับโค้ดที่เราจะรันในเบราว์เซอร์เท่านั้น

วิธีเปิดใช้งานฟีเจอร์เหล่านี้แตกต่างกันไปตาม IDE ของคุณ เราขอยกตัวอย่าง IDE ที่พบบ่อยบางตัวไว้ด้านล่าง หาก IDE ของคุณไม่อยู่ในรายการ โดยปกติคุณสามารถหาการตั้งค่าได้โดยค้นหา `rust-analyzer.cargo.features` หรือ `rust-analyzer.cargo.allFeatures`

VSCode ใน `settings.json`:
```json
{
  "rust-analyzer.cargo.features": "all",  // Enable all features
}
```

Neovim ใน `init.lua`:
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
helix ใน `.helix/languages.toml` หรือรายโปรเจกต์ใน `.helix/config.toml`:
```toml
[[language]]
name = "rust"

[language-server.rust-analyzer.config.cargo]
allFeatures = true
```

Zed ใน `settings.json`:

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

SublimeText 3 ใน user settings ของ LSP-rust-analyzer-settings.json
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


## 4) ตั้งค่า `leptosfmt` (ไม่บังคับ)

`leptosfmt` เป็นฟอร์แมตเตอร์สำหรับมาโคร `view!` ของ Leptos (ซึ่งคุณมักใช้เขียนโค้ด UI) เนื่องจากมาโคร `view!` ช่วยให้เขียน UI ในสไตล์ 'RSX' (คล้าย JSX) cargo-fmt จึงจัดรูปแบบโค้ดอัตโนมัติภายในมาโคร `view!` ได้ยากขึ้น `leptosfmt` เป็นครีตที่แก้ปัญหาการจัดรูปแบบของคุณ และทำให้โค้ด UI สไตล์ RSX ของคุณดูเรียบร้อยสวยงามอยู่เสมอ!

`leptosfmt` สามารถติดตั้งและใช้งานได้ผ่านบรรทัดคำสั่งหรือจากภายในเอดิเตอร์ของคุณ:

เริ่มแรก ติดตั้งเครื่องมือด้วย `cargo install leptosfmt`

หากคุณเพียงต้องการใช้ตัวเลือกเริ่มต้นจากบรรทัดคำสั่ง ก็แค่รัน `leptosfmt ./**/*.rs` จากรากของโปรเจกต์เพื่อจัดรูปแบบไฟล์ Rust ทั้งหมดด้วย `leptosfmt`

### รันอัตโนมัติใน IDE ที่ใช้ Rust Analyzer

หากคุณต้องการตั้งค่าเอดิเตอร์ให้ทำงานร่วมกับ `leptosfmt` หรือต้องการปรับแต่งประสบการณ์การใช้ `leptosfmt` ของคุณ โปรดดูคำแนะนำที่มีอยู่ใน[หน้า README.md ของรีโพ `leptosfmt` บน GitHub](https://github.com/bram209/leptosfmt)

โปรดทราบว่าแนะนำให้ตั้งค่าเอดิเตอร์ของคุณกับ `leptosfmt` เป็นรายเวิร์กสเปซเพื่อผลลัพธ์ที่ดีที่สุด

### รันอัตโนมัติใน RustRover

น่าเสียดายที่ RustRover ไม่รองรับ Rust Analyzer จึงต้องใช้แนวทางอื่นเพื่อรัน `leptosfmt` โดยอัตโนมัติ
วิธีหนึ่งคือใช้ปลั๊กอิน [FileWatchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) ด้วยการตั้งค่าดังนี้:

- Name: Leptosfmt
- File type: Rust files
- Program: `/path/to/leptosfmt` (ใช้แค่ `leptosfmt` ก็ได้หากอยู่ในตัวแปรสภาพแวดล้อม `$PATH` ของคุณ)
- Arguments: `$FilePath$`
- Output paths to refresh: `$FilePath$`


## 5) ใช้ `--cfg=erase_components` ระหว่างการพัฒนา

Leptos 0.7 ได้เปลี่ยนแปลงหลายอย่างในตัวเรนเดอร์ที่พึ่งพาระบบชนิดข้อมูลมากขึ้น สำหรับโปรเจกต์ขนาดใหญ่ สิ่งนี้อาจทำให้เวลาคอมไพล์ช้าลงได้ ความช้าของเวลาคอมไพล์ส่วนใหญ่สามารถบรรเทาได้โดยใช้แฟล็กการตั้งค่าแบบกำหนดเอง `--cfg=erase_components` ในระหว่างการพัฒนา (แฟล็กนี้จะลบข้อมูลชนิดข้อมูลบางส่วนออกเพื่อลดปริมาณงานที่ทำและข้อมูลดีบักที่คอมไพเลอร์ส่งออก โดยแลกมาด้วยขนาดไบนารีและค่าใช้จ่ายขณะรันที่เพิ่มขึ้น จึงไม่ควรใช้ในโหมด release)

ตั้งแต่ cargo-leptos v0.2.40 เป็นต้นมา ระบบจะเปิดใช้งานแฟล็กนี้ให้คุณโดยอัตโนมัติในโหมดพัฒนา หากคุณใช้ trunk ไม่ได้ใช้ cargo-leptos หรือต้องการเปิดใช้งานสำหรับการใช้งานที่ไม่ใช่การพัฒนา คุณสามารถตั้งค่าได้ง่ายๆ ในบรรทัดคำสั่ง (`RUSTFLAGS="--cfg erase_components" trunk serve` หรือ `RUSTFLAGS="--cfg erase_components" cargo leptos watch`) หรือใน `.cargo/config.toml` ของคุณ:
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
