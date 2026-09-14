# พารามิเตอร์และควิรี

พาธแบบคงที่มีประโยชน์สำหรับการแยกแยะระหว่างหน้าเพจต่าง ๆ แต่แอปพลิเคชันเกือบทุกตัวย่อมต้องการส่งผ่านข้อมูลทาง URL ในจุดใดจุดหนึ่ง

คุณสามารถทำสิ่งนี้ได้ 2 วิธี:

1. **พารามิเตอร์**ของเส้นทางที่มีชื่อ (named route params) เช่น `id` ใน `/users/:id`
2. **คิวรี**ของเส้นทางที่มีชื่อ (named route queries) เช่น `q` ใน `/search?q=Foo`

เนื่องจากลักษณะโครงสร้างของ URL คุณจึงสามารถเข้าถึงคิวรีได้จากวิวของ `<Route/>` *ทุกตัว* ส่วนพารามิเตอร์ของเส้นทางนั้น คุณสามารถเข้าถึงได้จาก `<Route/>` ที่นิยามมันไว้ หรือจากคอมโพเนนต์ลูกใด ๆ ที่ซ้อนอยู่ภายในมัน

การเข้าถึงพารามิเตอร์และคิวรีทำได้อย่างง่ายดายผ่านฮุกเหล่านี้:

- [`use_query`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_query.html) หรือ [`use_query_map`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_query_map.html)
- [`use_params`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_params.html) หรือ [`use_params_map`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_params_map.html)

แต่ละตัวจะมีทั้งรูปแบบที่ระบุชนิดข้อมูล (typed: `use_query` และ `use_params`) และรูปแบบที่ไม่ระบุชนิดข้อมูล (untyped: `use_query_map` และ `use_params_map`)

เวอร์ชันที่ไม่ระบุชนิดข้อมูลจะเก็บค่าเป็นคีย์-แมปอย่างง่าย ส่วนการใช้งานเวอร์ชันที่ระบุชนิดข้อมูล คุณจะต้องดีไรฟ์เทรต [`Params`](https://docs.rs/leptos_router/latest/leptos_router/params/trait.Params.html) ให้กับสตรัคต์ของคุณ

> `Params` เป็นเทรตที่มีขนาดเบามาก ใช้สำหรับแปลงแมปคีย์-ค่าแบบแบน (flat key-value map) ของสตริงให้กลายเป็นสตรัคต์ โดยการนำ `FromStr` ไปใช้กับแต่ละฟิลด์ และเนื่องจากโครงสร้างของพารามิเตอร์เส้นทางและคิวรีใน URL มีความแบน มันจึงมีความยืดหยุ่นน้อยกว่าไลบรารีอย่าง `serde` อย่างเห็นได้ชัด แต่ก็แลกมาด้วยการเพิ่มขนาดของไฟล์ไบนารีน้อยกว่ามากเช่นกัน

```rust
use leptos::Params;
use leptos_router::params::Params;

#[derive(Params, PartialEq)]
struct ContactParams {
    id: Option<usize>,
}

#[derive(Params, PartialEq)]
struct ContactSearch {
    q: Option<String>,
}
```

> หมายเหตุ: แมโครดีไรฟ์ `Params` อยู่ที่ `leptos_router::params::Params`
>
> เมื่อใช้ Rust เวอร์ชัน stable คุณจะใช้ได้เฉพาะ `Option<T>` ในพารามิเตอร์ แต่หากคุณเปิดใช้งานฟีเจอร์ `nightly`
> คุณจะสามารถใช้ได้ทั้ง `T` หรือ `Option<T>`

คราวนี้เราสามารถนำสิ่งเหล่านี้ไปใช้ในคอมโพเนนต์ได้แล้ว ลองนึกภาพ URL ที่มีทั้งพารามิเตอร์และคิวรี เช่น `/contacts/:id?q=Search`

เวอร์ชันที่ระบุชนิดข้อมูลจะคืนค่าเป็น `Memo<Result<T, _>>` ซึ่งการที่มันเป็น `Memo` ก็เพื่อให้ตอบสนองต่อการเปลี่ยนแปลงใน URL ได้แบบรีแอกทีฟ และการที่มันเป็น `Result` ก็เพราะพารามิเตอร์หรือคิวรีจะต้องถูกพาร์สจากสตริงใน URL จึงอาจได้ค่าที่ถูกต้องหรือไม่ก็ได้

```rust
use leptos_router::hooks::{use_params, use_query};

let params = use_params::<ContactParams>();
let query = use_query::<ContactSearch>();

// id: || -> usize
let id = move || {
    params
        .read()
        .as_ref()
        .ok()
        .and_then(|params| params.id)
        .unwrap_or_default()
};
```

เวอร์ชันที่ไม่ระบุชนิดข้อมูลจะคืนค่าเป็น `Memo<ParamsMap>` เช่นเดียวกัน ซึ่งเป็น `Memo` เพื่อตอบสนองต่อการเปลี่ยนแปลงใน URL โดย [`ParamsMap`](https://docs.rs/leptos_router/latest/leptos_router/params/struct.ParamsMap.html) ทำงานคล้ายกับแมปประเภทอื่น ๆ ทั่วไป โดยมีเมธอด `.get()` ที่คืนค่าเป็น `Option<String>`

```rust
use leptos_router::hooks::{use_params_map, use_query_map};

let params = use_params_map();
let query = use_query_map();

// id: || -> Option<String>
let id = move || params.read().get("id");
```

การทำแบบนี้อาจดูยุ่งยากอยู่บ้าง: การสร้างสัญญาณอนุพัทธ์ (derived signal) ที่ห่อหุ้ม `Option<_>` หรือ `Result<_>` อาจต้องผ่านขั้นตอนสองสามขั้นตอน แต่ก็คุ้มค่าที่จะทำด้วยเหตุผลสำคัญ 2 ประการ:

1. **ความถูกต้องแม่นยำ**: กล่าวคือ มันบังคับให้คุณต้องคำนึงถึงกรณีขอบ (edge cases) เช่น "ถ้าผู้ใช้ไม่ได้ส่งค่าสำหรับฟิลด์คิวรีนี้มาล่ะ? แล้วถ้าพวกเขาส่งค่าที่ไม่ถูกต้องมาล่ะ?"
2. **ประสิทธิภาพ**: โดยเฉพาะอย่างยิ่ง เมื่อคุณนำทางระหว่างพาธต่าง ๆ ที่ตรงกับคอมโพเนนต์ `<Route/>` ตัวเดิม โดยมีเพียงพารามิเตอร์หรือคิวรีเท่านั้นที่เปลี่ยนไป คุณจะได้รับการอัปเดตแบบละเอียดเฉพาะจุดไปยังส่วนต่าง ๆ ของแอปได้โดยไม่ต้องมีการเรนเดอร์ใหม่ทั้งคอมโพเนนต์ ตัวอย่างเช่น การนำทางระหว่างผู้ติดต่อคนต่าง ๆ ในตัวอย่างรายชื่อผู้ติดต่อของเรา จะทำการอัปเดตแบบเจาะจงเฉพาะที่ฟิลด์ชื่อ (และข้อมูลผู้ติดต่อ) โดยไม่จำเป็นต้องแทนที่หรือเรนเดอร์คอมโพเนนต์ `<Contact/>` ที่ห่อหุ้มอยู่ใหม่เลย นี่คือหัวใจและประโยชน์ของการอัปเดตแบบละเอียดระดับย่อย (fine-grained reactivity)

> นี่คือตัวอย่างเดียวกันกับในหัวข้อย่อยก่อนหน้า เนื่องจากระบบเราเตอร์มีการทำงานที่ผสานรวมกันอย่างมาก จึงสมเหตุสมผลที่จะใช้ตัวอย่างชุดเดียวในการสาธิตฟีเจอร์หลาย ๆ อย่าง แม้ว่าเราจะยังไม่ได้อธิบายฟีเจอร์ทั้งหมดในตอนนี้ก็ตาม

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/16-router-0-7-csm8t5?file=%2Fsrc%2Fmain.rs" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;
use leptos_router::components::{Outlet, ParentRoute, Route, Router, Routes, A};
use leptos_router::hooks::use_params_map;
use leptos_router::path;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <h1>"Contact App"</h1>
            // this <nav> will show on every routes,
            // because it's outside the <Routes/>
            // note: we can just use normal <a> tags
            // and the router will use client-side navigation
            <nav>
                <a href="/">"Home"</a>
                <a href="/contacts">"Contacts"</a>
            </nav>
            <main>
                <Routes fallback=|| "Not found.">
                    // / just has an un-nested "Home"
                    <Route path=path!("/") view=|| view! {
                        <h3>"Home"</h3>
                    }/>
                    // /contacts has nested routes
                    <ParentRoute
                        path=path!("/contacts")
                        view=ContactList
                      >
                        // if no id specified, fall back
                        <ParentRoute path=path!(":id") view=ContactInfo>
                            <Route path=path!("") view=|| view! {
                                <div class="tab">
                                    "(Contact Info)"
                                </div>
                            }/>
                            <Route path=path!("conversations") view=|| view! {
                                <div class="tab">
                                    "(Conversations)"
                                </div>
                            }/>
                        </ParentRoute>
                        // if no id specified, fall back
                        <Route path=path!("") view=|| view! {
                            <div class="select-user">
                                "Select a user to view contact info."
                            </div>
                        }/>
                    </ParentRoute>
                </Routes>
            </main>
        </Router>
    }
}

#[component]
fn ContactList() -> impl IntoView {
    view! {
        <div class="contact-list">
            // here's our contact list component itself
            <h3>"Contacts"</h3>
            <div class="contact-list-contacts">
                <A href="alice">"Alice"</A>
                <A href="bob">"Bob"</A>
                <A href="steve">"Steve"</A>
            </div>

            // <Outlet/> will show the nested child route
            // we can position this outlet wherever we want
            // within the layout
            <Outlet/>
        </div>
    }
}

#[component]
fn ContactInfo() -> impl IntoView {
    // we can access the :id param reactively with `use_params_map`
    let params = use_params_map();
    let id = move || params.read().get("id").unwrap_or_default();

    // imagine we're loading data from an API here
    let name = move || match id().as_str() {
        "alice" => "Alice",
        "bob" => "Bob",
        "steve" => "Steve",
        _ => "User not found.",
    };

    view! {
        <h4>{name}</h4>
        <div class="contact-info">
            <div class="tabs">
                <A href="" exact=true>"Contact Info"</A>
                <A href="conversations">"Conversations"</A>
            </div>

            // <Outlet/> here is the tabs that are nested
            // underneath the /contacts/:id route
            <Outlet/>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
