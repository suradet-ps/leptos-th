# คั่นรายการ: การจัดสไตล์

ใครก็ตามที่เริ่มลงมือสร้างเว็บไซต์หรือเว็บแอปพลิเคชัน ไม่ช้าก็เร็วจะต้องเผชิญกับคำถามเรื่องการจัดสไตล์ (styling) อย่างหลีกเลี่ยงไม่ได้ สำหรับแอปพลิเคชันขนาดเล็ก ไฟล์ CSS เพียงไฟล์เดียวก็อาจเพียงพอที่จะจัดแต่งหน้าตาอินเทอร์เฟซทั้งหมดได้ แต่เมื่อแอปเริ่มเติบโตและซับซ้อนขึ้น นักพัฒนาจำนวนมากพบว่าการเขียน CSS แบบดั้งเดิม (plain CSS) จะเริ่มยากต่อการดูแลรักษาและควบคุมระเบียบ

ฟรอนต์เอนด์เฟรมเวิร์กบางตัว (เช่น Angular, Vue และ Svelte) มาพร้อมกับกลไกจำกัดขอบเขตของ CSS (CSS scoping) ให้อยู่เฉพาะในแต่ละคอมโพเนนต์มาตั้งแต่แรก ทำให้การจัดการสไตล์ทั่วทั้งแอปพลิเคชันทำได้ง่ายขึ้นโดยไม่เกิดปัญหาสไตล์ของคอมโพเนนต์เล็ก ๆ ตัวหนึ่งหลุดไปกระทบส่วนอื่น ๆ ทั่วทั้งหน้าเว็บ (global side effects) ส่วนเฟรมเวิร์กอื่น ๆ (เช่น React หรือ Solid) ไม่ได้ใส่กลไกจำกัดขอบเขต CSS มาในตัว แต่จะพึ่งพาไลบรารีในระบบนิเวศภายนอกมาช่วยจัดการให้แทน ซึ่ง Leptos ก็จัดอยู่ในกลุ่มหลังนี้เช่นกัน: ตัวเฟรมเวิร์กไม่ได้กำหนดทิศทางหรือมีอคติใด ๆ เกี่ยวกับการเขียน CSS เลย แต่มอบเครื่องมือและพรีมิตีฟพื้นฐานไว้ให้ เพื่อให้ผู้อื่นสามารถนำไปต่อยอดสร้างไลบรารีสำหรับการจัดสไตล์ได้อย่างอิสระ

ด้านล่างนี้คือแนวทางหลากหลายรูปแบบในการจัดสไตล์ให้กับแอปพลิเคชัน Leptos ของคุณ โดยเริ่มจาก CSS ธรรมดาทั่วไป

## CSS ธรรมดา

### การเรนเดอร์ฝั่งไคลเอนต์ด้วย Trunk

`trunk` สามารถใช้รวบรวม (bundle) ไฟล์ CSS และรูปภาพต่าง ๆ เข้ากับโปรเจกต์เว็บไซต์ของคุณได้ โดยคุณสามารถประกาศพวกมันเป็นแอสเซ็ต (assets) ของ Trunk ได้โดยตรงในส่วน `<head>` ของไฟล์ `index.html` ตัวอย่างเช่น หากต้องการเพิ่มไฟล์ CSS ที่ตั้งอยู่ที่ `style.css` คุณสามารถใส่แท็ก `<link data-trunk rel="css" href="./style.css"/>` ได้ทันที

คุณสามารถศึกษาข้อมูลเพิ่มเติมได้จากเอกสารของ Trunk ในหัวข้อ [แอสเซ็ต](https://trunk-rs.github.io/trunk/guide/assets/index.html)

### การเรนเดอร์ฝั่งเซิร์ฟเวอร์ด้วย `cargo-leptos`

เทมเพลตเริ่มต้นของ `cargo-leptos` ได้รับการกำหนดค่าให้ใช้ SASS ในการบันเดิลไฟล์ CSS และส่งออกไปไว้ที่ `/pkg/{project_name}.css` โดยอัตโนมัติ หากคุณต้องการโหลดไฟล์ CSS เพิ่มเติม คุณสามารถทำได้โดยการอิมพอร์ตเข้าไปในไฟล์ `style.scss` นั้นโดยตรง หรือนำไฟล์ไปวางไว้ในไดเรกทอรี `public` (ตัวอย่างเช่น ไฟล์ที่อยู่ที่ `public/foo.css` จะสามารถเข้าถึงได้ผ่าน URL `/foo.css`)

หากต้องการโหลดสไตล์ชีตลงในคอมโพเนนต์ใดคอมโพเนนต์หนึ่งโดยเฉพาะ คุณสามารถใช้คอมโพเนนต์ [`Stylesheet`](https://docs.rs/leptos_meta/latest/leptos_meta/fn.Stylesheet.html) ได้

## TailwindCSS: CSS แบบยูทิลิตี-first

[TailwindCSS](https://tailwindcss.com/) เป็นไลบรารียอดนิยมที่ใช้แนวคิดแบบ utility-first ช่วยให้คุณสามารถจัดสไตล์ให้แอปพลิเคชันได้โดยตรงผ่านคลาสยูทิลิตีแบบอินไลน์ พร้อมทั้งมีเครื่องมือ CLI เฉพาะตัวที่คอยสแกนไฟล์ของคุณเพื่อค้นหาชื่อคลาส Tailwind แล้วนำมาสร้างเป็นไฟล์ CSS ที่จำเป็นให้โดยอัตโนมัติ

วิธีนี้ทำให้คุณสามารถเขียนคอมโพเนนต์ได้ในลักษณะนี้:

```rust
#[component]
fn Home() -> impl IntoView {
    let (count, set_count) = signal(0);

    view! {
        <main class="my-0 mx-auto max-w-3xl text-center">
            <h2 class="p-6 text-4xl">"Welcome to Leptos with Tailwind"</h2>
            <p class="px-10 pb-10 text-left">"Tailwind will scan your Rust files for Tailwind class names and compile them into a CSS file."</p>
            <button
                class="bg-sky-600 hover:bg-sky-700 px-5 py-3 text-white rounded-lg"
                on:click=move |_| *set_count.write() += 1
            >
                {move || if count.get() == 0 {
                    "Click me!".to_string()
                } else {
                    count.get().to_string()
                }}
            </button>
        </main>
    }
}
```

การตั้งค่าให้ Tailwind ทำงานร่วมกับโปรเจกต์อาจดูซับซ้อนเล็กน้อยในตอนแรก แต่คุณสามารถศึกษาแนวทางได้จากตัวอย่างของเรา ทั้งสำหรับการใช้ Tailwind กับ [แอปพลิเคชัน `trunk` ที่เรนเดอร์ฝั่งไคลเอนต์](https://github.com/leptos-rs/leptos/tree/main/examples/tailwind_csr) หรือกับ [แอปพลิเคชัน `cargo-leptos` ที่เรนเดอร์ฝั่งเซิร์ฟเวอร์](https://github.com/leptos-rs/leptos/tree/main/examples/tailwind_actix) นอกจากนี้ `cargo-leptos` ยังมี [การรองรับ Tailwind ในตัว](https://github.com/leptos-rs/cargo-leptos#site-parameters) ซึ่งคุณสามารถเลือกใช้เป็นทางเลือกแทน CLI ของ Tailwind ได้เช่นกัน

## Stylers: การสกัด CSS ตอนคอมไพล์

[Stylers](https://github.com/abishekatp/stylers) เป็นไลบรารี CSS แบบกำหนดขอบเขตในระหว่างขั้นตอนคอมไพล์ (compile-time scoped CSS) ที่เปิดโอกาสให้คุณประกาศสไตล์ CSS ที่จำกัดขอบเขตไว้ภายในเนื้อหาของคอมโพเนนต์ได้โดยตรง โดย Stylers จะทำการสกัดโค้ด CSS เหล่านี้ออกมาเป็นไฟล์ CSS แยกต่างหากในตอนคอมไพล์ ซึ่งคุณสามารถนำเข้าสู่แอปพลิเคชันได้ในภายหลัง ส่งผลให้ไม่มีผลกระทบต่อขนาดของไบนารี WASM เลยแม้แต่น้อย

สิ่งนี้ช่วยให้คุณสามารถเขียนคอมโพเนนต์ในรูปแบบนี้ได้:

```rust
use stylers::style;

#[component]
pub fn App() -> impl IntoView {
    let styler_class = style! { "App",
        ##two{
            color: blue;
        }
        div.one{
            color: red;
            content: raw_str(r#"\hello"#);
            font: "1.3em/1.2" Arial, Helvetica, sans-serif;
        }
        div {
            border: 1px solid black;
            margin: 25px 50px 75px 100px;
            background-color: lightblue;
        }
        h2 {
            color: purple;
        }
        @media only screen and (max-width: 1000px) {
            h3 {
                background-color: lightblue;
                color: blue
            }
        }
    };

    view! { class = styler_class,
        <div class="one">
            <h1 id="two">"Hello"</h1>
            <h2>"World"</h2>
            <h2>"and"</h2>
            <h3>"friends!"</h3>
        </div>
    }
}
```

## Stylance: CSS แบบจำกัดขอบเขตที่เขียนในไฟล์ CSS

ในขณะที่ Stylers ให้คุณเขียน CSS แบบอินไลน์ในโค้ด Rust แล้วสกัดออกมาตอนคอมไพล์ ไลบรารี [Stylance](https://github.com/basro/stylance-rs) จะเปิดโอกาสให้คุณเขียน CSS แยกเป็นไฟล์ภายนอกเคียงข้างกับคอมโพเนนต์ของคุณ แล้วจึงอิมพอร์ตไฟล์เหล่านั้นเข้ามายังคอมโพเนนต์ พร้อมทั้งจำกัดขอบเขตของคลาส CSS ให้มีผลเฉพาะภายในคอมโพเนนต์นั้น ๆ

แนวทางนี้ทำงานร่วมกับฟีเจอร์ live-reloading ของทั้ง `trunk` และ `cargo-leptos` ได้อย่างยอดเยี่ยม เพราะไฟล์ CSS ที่ได้รับการแก้ไขจะแสดงผลลัพธ์ใหม่บนเบราว์เซอร์ได้ทันที

```rust
import_style!(style, "app.module.scss");

#[component]
fn HomePage() -> impl IntoView {
    view! {
        <div class=style::jumbotron/>
    }
}
```

คุณสามารถแก้ไขโค้ด CSS ได้โดยตรงโดยไม่ต้องรอให้โค้ด Rust ทำการคอมไพล์ใหม่เลย:

```css
.jumbotron {
  background: blue;
}
```

## Styled: การจำกัดขอบเขต CSS ตอนรันไทม์

[Styled](https://github.com/eboody/styled) เป็นไลบรารี CSS แบบจำกัดขอบเขตในระหว่างการทำงาน (runtime scoped CSS) ที่ผสานรวมกับ Leptos ได้อย่างราบรื่น ช่วยให้คุณสามารถประกาศ CSS ที่จำกัดขอบเขตไว้ในฟังก์ชันคอมโพเนนต์ และนำสไตล์เหล่านั้นไปประยุกต์ใช้ในตอนรันไทม์

```rust

use styled::style;



#[component]

pub fn MyComponent() -> impl IntoView {

    let styles = style!(

      div {

        background-color: red;

        color: white;

      }

    );



    styled::view! { styles,

        <div>"This text should be red with white text."</div>

    }

}

```

## ยินดีรับการมีส่วนร่วม

Leptos ไม่ได้มีกฎเกณฑ์ตายตัวว่าคุณควรจัดสไตล์เว็บไซต์หรือแอปพลิเคชันของคุณอย่างไร แต่เรายินดีอย่างยิ่งที่จะสนับสนุนเครื่องมือต่าง ๆ ที่คุณพัฒนาขึ้นเพื่อช่วยให้การทำงานนี้สะดวกสบายยิ่งขึ้น หากคุณกำลังพัฒนาแนวทางการเขียน CSS หรือการจัดสไตล์รูปแบบใหม่ ๆ ที่อยากแบ่งปันให้ปรากฏอยู่ในรายการนี้ โปรดแจ้งให้เราทราบได้ตลอดเวลา!
