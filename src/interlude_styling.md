# คั่นรายการ: การจัดสไตล์

ใครก็ตามที่สร้างเว็บไซต์หรือแอปพลิเคชันมักเจอคำถามเรื่องการจัดสไตล์ในไม่ช้า สำหรับแอปขนาดเล็ก ไฟล์ CSS ไฟล์เดียวก็เพียงพอสำหรับจัดสไตล์ส่วนติดต่อผู้ใช้ของคุณ แต่เมื่อแอปพลิเคชันเติบโตขึ้น นักพัฒนาหลายคนพบว่า CSS ธรรมดาจัดการได้ยากขึ้นเรื่อยๆ

ฟรอนต์เอนด์เฟรมเวิร์กบางตัว (เช่น Angular, Vue และ Svelte) มีวิธีในตัวสำหรับจำกัดขอบเขต CSS ให้กับคอมโพเนนต์ที่ต้องการ ทำให้จัดการสไตล์ทั่วทั้งแอปพลิเคชันได้ง่ายขึ้น โดยสไตล์ที่ตั้งใจแก้ไขคอมโพเนนต์เล็กๆ ตัวหนึ่งจะไม่ส่งผลในระดับส่วนกลาง เฟรมเวิร์กอื่นๆ (เช่น React หรือ Solid) ไม่มีกลไกจำกัดขอบเขต CSS ในตัว แต่พึ่งพาไลบรารีในระบบนิเวศให้ทำแทน Leptos อยู่ในกลุ่มหลังนี้: ตัวเฟรมเวิร์กไม่มีความคิดเห็นใดๆ เกี่ยวกับ CSS เลย แต่มีเครื่องมือและพรีมิทีฟบางอย่างที่ให้ผู้อื่นสร้างไลบรารีสำหรับจัดสไตล์ได้

นี่คือแนวทางต่างๆ ในการจัดสไตล์แอป Leptos ของคุณ เริ่มจาก CSS ธรรมดา

## CSS ธรรมดา

### การเรนเดอร์ฝั่งไคลเอนต์ด้วย Trunk

`trunk` ใช้รวมไฟล์ CSS และรูปภาพเข้ากับไซต์ของคุณได้ ในการทำเช่นนี้ คุณเพิ่มพวกมันเป็นแอสเซ็ตของ Trunk โดยนิยามไว้ใน `index.html` ส่วน `<head>` ตัวอย่างเช่น หากต้องการเพิ่มไฟล์ CSS ที่อยู่ที่ `style.css` คุณสามารถเพิ่มแท็ก `<link data-trunk rel="css" href="./style.css"/>` ได้

คุณดูข้อมูลเพิ่มเติมได้ในเอกสารของ Trunk เกี่ยวกับ[แอสเซ็ต](https://trunk-rs.github.io/trunk/guide/assets/index.html)

### การเรนเดอร์ฝั่งเซิร์ฟเวอร์ด้วย `cargo-leptos`

เทมเพลตของ `cargo-leptos` ถูกตั้งค่าเริ่มต้นให้ใช้ SASS ในการรวมไฟล์ CSS และส่งออกไปที่ `/pkg/{project_name}.css` หากคุณต้องการโหลดไฟล์ CSS เพิ่มเติม คุณทำได้โดยนำเข้าพวกมันในไฟล์ `style.scss` นั้น หรือเพิ่มลงในไดเรกทอรี `public` (ตัวอย่างเช่น ไฟล์ที่ `public/foo.css` จะถูกเสิร์ฟที่ `/foo.css`)

หากต้องการโหลดสไตล์ชีตในคอมโพเนนต์ คุณใช้คอมโพเนนต์ [`Stylesheet`](https://docs.rs/leptos_meta/latest/leptos_meta/fn.Stylesheet.html) ได้

## TailwindCSS: CSS แบบยูทิลิตี-first

[TailwindCSS](https://tailwindcss.com/) เป็นไลบรารี CSS แบบ utility-first ที่ได้รับความนิยม มันให้คุณจัดสไตล์แอปพลิเคชันด้วยคลาสยูทิลิตีแบบอินไลน์ พร้อมเครื่องมือ CLI เฉพาะที่สแกนหาชื่อคลาส Tailwind ในไฟล์ของคุณแล้วรวม CSS ที่จำเป็นให้

สิ่งนี้ทำให้คุณเขียนคอมโพเนนต์แบบนี้ได้:

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

ตอนแรกการตั้งค่าการผสานรวม Tailwind อาจดูซับซ้อนสักหน่อย แต่คุณดูตัวอย่างสองตัวอย่างของเราเกี่ยวกับวิธีใช้ Tailwind กับ[แอปพลิเคชัน `trunk` ที่เรนเดอร์ฝั่งไคลเอนต์](https://github.com/leptos-rs/leptos/tree/main/examples/tailwind_csr) หรือกับ[แอปพลิเคชัน `cargo-leptos` ที่เรนเดอร์ฝั่งเซิร์ฟเวอร์](https://github.com/leptos-rs/leptos/tree/main/examples/tailwind_actix) ได้ `cargo-leptos` ยังมี[การรองรับ Tailwind ในตัว](https://github.com/leptos-rs/cargo-leptos#site-parameters)บางส่วนที่คุณใช้เป็นทางเลือกแทน CLI ของ Tailwind ได้ด้วย

## Stylers: การสกัด CSS ตอนคอมไพล์

[Stylers](https://github.com/abishekatp/stylers) เป็นไลบรารี CSS แบบจำกัดขอบเขตที่ทำงานตอนคอมไพล์ ซึ่งให้คุณประกาศ CSS ที่จำกัดขอบเขตในเนื้อหาของคอมโพเนนต์ได้ Stylers จะสกัด CSS นี้ออกมาตอนคอมไพล์เป็นไฟล์ CSS ที่คุณนำเข้าแอปได้ในภายหลัง ซึ่งหมายความว่ามันไม่เพิ่มขนาดไบนารี WASM ของแอปพลิเคชันคุณเลย

สิ่งนี้ทำให้คุณเขียนคอมโพเนนต์แบบนี้ได้:

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

Stylers ให้คุณเขียน CSS แบบอินไลน์ในโค้ด Rust สกัดมันออกมาตอนคอมไพล์ และจำกัดขอบเขตให้ [Stylance](https://github.com/basro/stylance-rs) ให้คุณเขียน CSS ในไฟล์ CSS เคียงข้างคอมโพเนนต์ นำไฟล์เหล่านั้นเข้าสู่คอมโพเนนต์ และจำกัดขอบเขตคลาส CSS ให้กับคอมโพเนนต์ของคุณ

วิธีนี้ทำงานร่วมกับฟีเจอร์โหลดสดของ `trunk` และ `cargo-leptos` ได้ดี เพราะไฟล์ CSS ที่แก้ไขจะอัปเดตในเบราว์เซอร์ได้ทันที

```rust
import_style!(style, "app.module.scss");

#[component]
fn HomePage() -> impl IntoView {
    view! {
        <div class=style::jumbotron/>
    }
}
```

คุณแก้ไข CSS ได้โดยตรงโดยไม่ต้องคอมไพล์ Rust ใหม่

```css
.jumbotron {
  background: blue;
}
```


## Styled: การจำกัดขอบเขต CSS ตอนรันไทม์



[Styled](https://github.com/eboody/styled) เป็นไลบรารี CSS แบบจำกัดขอบเขตตอนรันไทม์ที่ผสานรวมกับ Leptos ได้ดี มันให้คุณประกาศ CSS ที่จำกัดขอบเขตในเนื้อหาของฟังก์ชันคอมโพเนนต์ แล้วนำสไตล์เหล่านั้นไปใช้ตอนรันไทม์



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

Leptos ไม่มีความคิดเห็นใดๆ เกี่ยวกับวิธีการจัดสไตล์เว็บไซต์หรือแอปของคุณ แต่เรายินดีอย่างยิ่งที่จะสนับสนุนเครื่องมือใดๆ ที่คุณพยายามสร้างขึ้นเพื่อให้เรื่องนี้ง่ายขึ้น หากคุณกำลังทำแนวทาง CSS หรือการจัดสไตล์ที่อยากเพิ่มลงในรายการนี้ โปรดบอกเราให้ทราบ!
