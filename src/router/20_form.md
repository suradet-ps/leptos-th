# คอมโพเนนต์ `<Form/>`

ลิงก์และฟอร์มบางครั้งดูเหมือนไม่เกี่ยวข้องกันเลย แต่จริงๆ แล้ว พวกมันทำงานในลักษณะที่คล้ายกันมาก

ใน HTML ธรรมดา มีสามวิธีในการนำทางไปยังหน้าอื่น:

1. เอลิเมนต์ `<a>` ที่ลิงก์ไปยังหน้าอื่น: นำทางไปยัง URL ในแอตทริบิวต์ `href` ของมันด้วยเมธอด HTTP `GET`
2. `<form method="GET">`: นำทางไปยัง URL ในแอตทริบิวต์ `action` ของมันด้วยเมธอด HTTP `GET` โดยข้อมูลฟอร์มจากอินพุตถูกเข้ารหัสไว้ในสตริงควิรีของ URL
3. `<form method="POST">`: นำทางไปยัง URL ในแอตทริบิวต์ `action` ของมันด้วยเมธอด HTTP `POST` โดยข้อมูลฟอร์มจากอินพุตถูกเข้ารหัสไว้ในบอดีของคำขอ

เนื่องจากเรามีเราเตอร์ฝั่งไคลเอนต์ เราจึงทำการนำทางลิงก์ฝั่งไคลเอนต์ได้โดยไม่ต้องรีโหลดหน้าเพจ กล่าวคือ โดยไม่ต้องเดินทางไปกลับเซิร์ฟเวอร์เต็มรูปแบบ จึงสมเหตุสมผลที่เราจะทำการนำทางฟอร์มฝั่งไคลเอนต์ได้ในลักษณะเดียวกัน

เราเตอร์จัดเตรียมคอมโพเนนต์ [`<Form>`](https://docs.rs/leptos_router/latest/leptos_router/components/fn.Form.html) ซึ่งทำงานเหมือนเอลิเมนต์ `<form>` ของ HTML แต่ใช้การนำทางฝั่งไคลเอนต์แทนการรีโหลดหน้าเต็ม `<Form/>` ทำงานได้กับทั้งคำขอ `GET` และ `POST` ด้วย `method="GET"` มันจะนำทางไปยัง URL ที่ถูกเข้ารหัสในข้อมูลฟอร์ม ด้วย `method="POST"` มันจะส่งคำขอ `POST` และจัดการการตอบกลับของเซิร์ฟเวอร์

`<Form/>` เป็นรากฐานให้กับคอมโพเนนต์บางอย่างอย่าง `<ActionForm/>` และ `<MultiActionForm/>` ที่เราจะได้เห็นในบทต่อๆ ไป แต่มันยังเปิดใช้รูปแบบการใช้งานที่ทรงพลังของตัวเองด้วย

ตัวอย่างเช่น ลองนึกภาพว่าคุณต้องการสร้างช่องค้นหาที่อัปเดตผลการค้นหาแบบเรียลไทม์ขณะที่ผู้ใช้ค้นหา โดยไม่รีโหลดหน้าเพจ แต่ยังเก็บการค้นหาไว้ใน URL เพื่อให้ผู้ใช้คัดลอกไปวางแชร์ผลลัพธ์กับคนอื่นได้

ปรากฏว่ารูปแบบที่เราเรียนมาแล้วจนถึงตอนนี้ทำให้สิ่งนี้ง่ายต่อการนำไปใช้

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

ทุกครั้งที่คุณคลิก `Submit` ตัว `<Form/>` จะ “นำทาง” ไปยัง `?q={search}` แต่เนื่องจากการนำทางนี้ทำฝั่งไคลเอนต์ จึงไม่มีการกระพริบหรือรีโหลดหน้าเพจ สตริงควิรีของ URL เปลี่ยนแปลง ซึ่งกระตุ้นให้ `search` อัปเดต เพราะ `search` เป็นสัญญาณต้นทางของรีซอร์ส `search_results` สิ่งนี้จึงกระตุ้นให้ `search_results` โหลดรีซอร์สของมันใหม่ ตัว `<Transition/>` จะแสดงผลการค้นหาปัจจุบันต่อไปจนกว่าผลใหม่จะโหลดเสร็จ เมื่อโหลดเสร็จแล้ว มันจะสลับไปแสดงผลลัพธ์ใหม่

นี่เป็นรูปแบบที่ยอดเยี่ยม โฟลว์ข้อมูลชัดเจนมาก: ข้อมูลทั้งหมดไหลจาก URL ไปยังรีซอร์สเข้าสู่ UI สถานะปัจจุบันของแอปพลิเคชันถูกเก็บไว้ใน URL ซึ่งหมายความว่าคุณสามารถรีเฟรชหน้าเพจหรือส่งลิงก์ให้เพื่อนทางข้อความ แล้วมันจะแสดงสิ่งที่คุณคาดหวังไว้อย่างแม่นยำ และเมื่อเราแนะนำการเรนเดอร์ฝั่งเซิร์ฟเวอร์ รูปแบบนี้จะพิสูจน์ว่าทนทานต่อข้อผิดพลาดได้จริงๆ ด้วย เพราะมันใช้เอลิเมนต์ `<form>` และ URL ภายใต้ฮู้ด มันจึงทำงานได้ดีจริงๆ แม้จะไม่ได้โหลด WASM ของคุณบนไคลเอนต์ด้วยซ้ำ

ที่จริงเรายังไปได้อีกขั้นและทำอะไรที่ค่อนข้างฉลาด:

```rust
view! {
	<Form method="GET" action="">
		<input type="search" name="q" value=search
			oninput="this.form.requestSubmit()"
		/>
	</Form>
}
```

คุณจะสังเกตว่าเวอร์ชันนี้ตัดปุ่ม `Submit` ออกไป แทนที่นั้น เราเพิ่มแอตทริบิวต์ `oninput` ให้อินพุต สังเกตว่านี่_ไม่ใช่_ `on:input` ซึ่งจะรับฟังเหตุการณ์ `input` และรันโค้ด Rust บางอย่าง หากไม่มีเครื่องหมายทวิภาค `oninput` คือแอตทริบิวต์ HTML ธรรมดา ดังนั้นสตริงนี้จึงเป็นสตริง JavaScript จริงๆ `this.form` ให้ฟอร์มที่อินพุตผูกอยู่ด้วย `requestSubmit()` จะยิงเหตุการณ์ `submit` บน `<form>` ซึ่งถูกดักจับโดย `<Form/>` ราวกับว่าเราได้คลิกปุ่ม `Submit` ตอนนี้ฟอร์มจะ “นำทาง” ทุกครั้งที่มีการกดคีย์หรืออินพุต เพื่อให้ URL (และดังนั้นการค้นหา) ซิงก์กับการป้อนข้อมูลของผู้ใช้อย่างสมบูรณ์แบบขณะที่พวกเขาพิมพ์

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
