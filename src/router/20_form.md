# คอมโพเนนต์ `<Form/>`

ลิงก์และแบบฟอร์มบางครั้งอาจดูเหมือนไม่เกี่ยวข้องกันเลย แต่จริง ๆ แล้วพวกมันทำงานในลักษณะที่คล้ายคลึงกันอย่างมาก

ใน HTML ทั่วไป มีวิธีนำทางไปยังหน้าอื่นอยู่ 3 วิธี:

1. เอลิเมนต์ `<a>` ที่ลิงก์ไปยังหน้าอื่น: จะนำทางไปยัง URL ที่ระบุในแอตทริบิวต์ `href` ด้วยเมธอด HTTP `GET`
2. `<form method="GET">`: จะนำทางไปยัง URL ที่ระบุในแอตทริบิวต์ `action` ด้วยเมธอด HTTP `GET` โดยนำข้อมูลฟอร์มจากช่องอินพุตต่าง ๆ ไปเข้ารหัส (encode) ไว้ใน query string ของ URL
3. `<form method="POST">`: จะนำทางไปยัง URL ที่ระบุในแอตทริบิวต์ `action` ด้วยเมธอด HTTP `POST` โดยนำข้อมูลฟอร์มจากช่องอินพุตต่าง ๆ ไปเข้ารหัสไว้ในเนื้อหาคำขอ (request body)

และเนื่องจากเรามีระบบเราเตอร์บนฝั่งไคลเอนต์ เราจึงสามารถนำทางผ่านลิงก์บนฝั่งไคลเอนต์ได้โดยไม่ต้องรีโหลดหน้าเว็บใหม่ กล่าวคือ ไม่ต้องส่งคำขอแบบไป-กลับ (round-trip) ไปยังเซิร์ฟเวอร์เต็มรูปแบบ จึงสมเหตุสมผลอย่างยิ่งที่เราจะสามารถนำทางผ่านแบบฟอร์มบนฝั่งไคลเอนต์ได้ในลักษณะเดียวกันนี้

เราเตอร์มีคอมโพเนนต์ [`<Form>`](https://docs.rs/leptos_router/latest/leptos_router/components/fn.Form.html) ซึ่งทำงานเหมือนกับเอลิเมนต์ `<form>` ปกติของ HTML ทุกประการ แต่เปลี่ยนมาใช้การนำทางบนฝั่งไคลเอนต์แทนการรีโหลดหน้าเว็บใหม่ทั้งหมด โดย `<Form/>` รองรับทั้งคำขอแบบ `GET` และ `POST`: เมื่อระบุ `method="GET"` มันจะนำทางไปยัง URL ที่ถูกเข้ารหัสข้อมูลจากฟอร์มเอาไว้ ส่วนเมื่อระบุ `method="POST"` มันจะส่งคำขอ `POST` ออกไปและคอยจัดการผลลัพธ์ตอบกลับจากเซิร์ฟเวอร์

`<Form/>` เป็นรากฐานสำคัญให้กับคอมโพเนนต์ต่าง ๆ เช่น `<ActionForm/>` และ `<MultiActionForm/>` ที่เราจะได้พบกันในบทต่อ ๆ ไป แต่ตัวมันเองก็รองรับรูปแบบการใช้งาน (patterns) ที่ทรงพลังในตัวเองอยู่แล้ว

ตัวอย่างเช่น ลองนึกภาพว่าคุณต้องการสร้างช่องค้นหาที่อัปเดตผลลัพธ์แบบเรียลไทม์ขณะที่ผู้ใช้กำลังพิมพ์ค้นหา โดยไม่มีการรีโหลดหน้าเว็บ แต่ในขณะเดียวกันก็ยังคงบันทึกคำค้นหานั้นไว้ใน URL เพื่อให้ผู้ใช้สามารถคัดลอกลิงก์ไปแชร์ผลลัพธ์ให้เพื่อนได้ทันที

ปรากฏว่ารูปแบบที่เราได้เรียนรู้กันมาจนถึงตอนนี้ ทำให้การสร้างฟังก์ชันดังกล่าวเป็นเรื่องง่ายดายมาก:

```rust
async fn fetch_results() {
    // some async function to fetch our search results
}

#[component]
pub fn FormExample() -> impl IntoView {
    // reactive access to URL query strings
    let query = use_query_map();
    // search stored as ?q=
    let search = move || query.read().get("q").unwrap_or_default();
    // a resource driven by the search string
    let search_results = Resource::new(search, |_| fetch_results());

    view! {
        <Form method="GET" action="">
            <input type="search" name="q" value=search/>
            <input type="submit"/>
        </Form>
        <Transition fallback=move || ()>
            /* render search results */
            {todo!()}
        </Transition>
    }
}
```

ทุกครั้งที่คุณคลิกปุ่ม `Submit` ตัว `<Form/>` จะทำการ "นำทาง" ไปยัง `?q={search}` แต่เนื่องจากการนำทางนี้เกิดขึ้นบนฝั่งไคลเอนต์ จึงไม่มีอาการหน้าจอกะพริบหรือการรีโหลดหน้าเว็บเลย โดยสตริงคิวรีของ URL จะเปลี่ยนไป ซึ่งจะไปกระตุ้นให้สัญญาณ `search` อัปเดต และเนื่องจาก `search` เป็นสัญญาณต้นทางของรีซอร์ส `search_results` จึงทำให้ `search_results` สั่งโหลดข้อมูลใหม่อีกครั้ง ในระหว่างนั้น คอมโพเนนต์ `<Transition/>` จะยังคงแสดงผลการค้นหาเดิมต่อไปจนกว่าผลลัพธ์ใหม่จะโหลดเสร็จสมบูรณ์ และเมื่อเสร็จแล้วจึงจะสลับมาแสดงผลลัพธ์ใหม่อย่างราบรื่น

นี่คือรูปแบบการออกแบบที่ยอดเยี่ยมมาก โฟลว์ของข้อมูลมีความชัดเจนอย่างยิ่ง: ข้อมูลทั้งหมดจะไหลจาก URL ไปยังรีซอร์ส แล้วเข้าสู่ UI โดยตรง สถานะปัจจุบันของแอปพลิเคชันถูกบันทึกไว้ใน URL อย่างสมบูรณ์ ซึ่งหมายความว่าคุณสามารถรีเฟรชหน้าเว็บ หรือส่งลิงก์ให้เพื่อนทางแชต แล้วปลายทางก็จะเห็นหน้าจอตรงกับที่คุณเห็นทุกประการ และเมื่อเราก้าวไปสู่เรื่องการเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR) รูปแบบนี้จะพิสูจน์ให้เห็นว่ามีความทนทานต่อข้อผิดพลาด (fault-tolerant) อย่างแท้จริง เพราะเบื้องหลังการทำงานยังคงใช้เอลิเมนต์ `<form>` และ URL ตามมาตรฐานเว็บ มันจึงสามารถทำงานได้เป็นอย่างดีแม้กระทั่งก่อนที่ไฟล์ WASM จะโหลดเสร็จบนเบราว์เซอร์ด้วยซ้ำ

ยิ่งไปกว่านั้น เรายังสามารถต่อยอดให้ชาญฉลาดยิ่งขึ้นไปอีกขั้นได้ดังนี้:

```rust
view! {
	<Form method="GET" action="">
		<input type="search" name="q" value=search
			oninput="this.form.requestSubmit()"
		/>
	</Form>
}
```

คุณจะสังเกตเห็นว่าในเวอร์ชันนี้เราตัดปุ่ม `Submit` ออกไป แล้วแทนที่ด้วยการเพิ่มแอตทริบิวต์ `oninput` ลงไปในช่องอินพุต โปรดสังเกตว่านี่ *ไม่ใช่* `on:input` (ซึ่งเป็นการดักฟังเหตุการณ์ `input` แล้วรันโค้ดภาษา Rust) หากไม่มีเครื่องหมายทวิภาค (`:`) แอตทริบิวต์ `oninput` จะเป็นแอตทริบิวต์ HTML ทั่วไป ดังนั้นข้อความสตริงนี้จึงเป็นโค้ด JavaScript จริง ๆ โดย `this.form` จะอ้างอิงถึงฟอร์มที่อินพุตนั้นสังกัดอยู่ และฟังก์ชัน `requestSubmit()` จะสั่งยิงเหตุการณ์ `submit` บน `<form>` ซึ่งจะถูกดักจับโดยคอมโพเนนต์ `<Form/>` เสมือนว่าผู้ใช้ได้คลิกปุ่ม `Submit` จริง ๆ ส่งผลให้แบบฟอร์มทำการ "นำทาง" ในทุก ๆ ครั้งที่มีการกดแป้นพิมพ์หรือพิมพ์ข้อมูล ทำให้ URL (และผลการค้นหา) ซิงก์ตรงกับข้อความที่ผู้ใช้พิมพ์ในทันทีแบบเรียลไทม์

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/20-form-0-7-m73jsz)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/20-form-0-7-m73jsz" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;
use leptos_router::components::{Form, Route, Router, Routes};
use leptos_router::hooks::use_query_map;
use leptos_router::path;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <h1><code>"<Form/>"</code></h1>
            <main>
                <Routes fallback=|| "Not found.">
                    <Route path=path!("") view=FormExample/>
                </Routes>
            </main>
        </Router>
    }
}

#[component]
pub fn FormExample() -> impl IntoView {
    // reactive access to URL query
    let query = use_query_map();
    let name = move || query.read().get("name").unwrap_or_default();
    let number = move || query.read().get("number").unwrap_or_default();
    let select = move || query.read().get("select").unwrap_or_default();

    view! {
        // read out the URL query strings
        <table>
            <tr>
                <td><code>"name"</code></td>
                <td>{name}</td>
            </tr>
            <tr>
                <td><code>"number"</code></td>
                <td>{number}</td>
            </tr>
            <tr>
                <td><code>"select"</code></td>
                <td>{select}</td>
            </tr>
        </table>
        // <Form/> will navigate whenever submitted
        <h2>"Manual Submission"</h2>
        <Form method="GET" action="">
            // input names determine query string key
            <input type="text" name="name" value=name/>
            <input type="number" name="number" value=number/>
            <select name="select">
                // `selected` will set which starts as selected
                <option selected=move || select() == "A">
                    "A"
                </option>
                <option selected=move || select() == "B">
                    "B"
                </option>
                <option selected=move || select() == "C">
                    "C"
                </option>
            </select>
            // submitting should cause a client-side
            // navigation, not a full reload
            <input type="submit"/>
        </Form>
        // This <Form/> uses some JavaScript to submit
        // on every input
        <h2>"Automatic Submission"</h2>
        <Form method="GET" action="">
            <input
                type="text"
                name="name"
                value=name
                // this oninput attribute will cause the
                // form to submit on every input to the field
                oninput="this.form.requestSubmit()"
            />
            <input
                type="number"
                name="number"
                value=number
                oninput="this.form.requestSubmit()"
            />
            <select name="select"
                onchange="this.form.requestSubmit()"
            >
                <option selected=move || select() == "A">
                    "A"
                </option>
                <option selected=move || select() == "B">
                    "B"
                </option>
                <option selected=move || select() == "C">
                    "C"
                </option>
            </select>
            // submitting should cause a client-side
            // navigation, not a full reload
            <input type="submit"/>
        </Form>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
