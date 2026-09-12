# พารามิเตอร์และควิรี

พาธแบบคงที่มีประโยชน์สำหรับการแยกแยะระหว่างหน้าเพจต่างๆ แต่แอปพลิเคชันเกือบทุกตัวต้องการส่งข้อมูลผ่าน URL ในบางจุด

คุณทำเช่นนี้ได้สองวิธี:

1. **พารามิเตอร์**ของเส้นทางที่มีชื่อ อย่าง `id` ใน `/users/:id`
2. **ควิรี**ของเส้นทางที่มีชื่อ อย่าง `q` ใน `/search?q=Foo`

เนื่องจากวิธีที่ URL ถูกสร้างขึ้น คุณสามารถเข้าถึงควิรีได้จากวิวของ `<Route/>`_ทุกตัว_ คุณสามารถเข้าถึงพารามิเตอร์ของเส้นทางได้จาก `<Route/>` ที่นิยามมันไว้ หรือจาก children แบบซ้อนใดๆ ของมัน

การเข้าถึงพารามิเตอร์และควิรีนั้นง่ายมากด้วยฮุกสองสามตัว:

- [`use_query`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_query.html) หรือ [`use_query_map`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_query_map.html)
- [`use_params`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_params.html) หรือ [`use_params_map`](https://docs.rs/leptos_router/latest/leptos_router/hooks/fn.use_params_map.html)

แต่ละตัวมีแบบที่ระบุชนิด (`use_query` และ `use_params`) และแบบที่ไม่ระบุชนิด (`use_query_map` และ `use_params_map`)

เวอร์ชันที่ไม่ระบุชนิดเก็บแผนที่คีย์-ค่าแบบง่ายๆ การจะใช้เวอร์ชันที่ระบุชนิด ให้ดีไรฟ์แทรต [`Params`](https://docs.rs/leptos_router/latest/leptos_router/params/trait.Params.html) บนสตรัคต์

> `Params` เป็นแทรตที่เบามากสำหรับแปลงแผนที่คีย์-ค่าแบบแบนของสตริงให้เป็นสตรัคต์ โดยการนำ `FromStr` ไปใช้กับแต่ละฟิลด์ เนื่องจากโครงสร้างแบบแบนของพารามิเตอร์เส้นทางและควิรีของ URL มันจึงยืดหยุ่นน้อยกว่าสิ่งอย่าง `serde` อย่างมีนัยสำคัญ และยังเพิ่มน้ำหนักให้ไบนารีของคุณน้อยกว่ามากด้วย

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

> หมายเหตุ: มาโครดีไรฟ์ `Params` อยู่ที่ `leptos_router::params::Params`
>
> เมื่อใช้ stable คุณใช้ได้เฉพาะ `Option<T>` ในพารามิเตอร์ หากคุณใช้ฟีเจอร์ `nightly`
> คุณใช้ได้ทั้ง `T` หรือ `Option<T>`

ตอนนี้เราสามารถใช้พวกมันในคอมโพเนนต์ได้ ลองนึกภาพ URL ที่มีทั้งพารามิเตอร์และควิรี อย่าง `/contacts/:id?q=Search`

เวอร์ชันที่ระบุชนิดคืนค่า `Memo<Result<T, _>>` มันเป็น `Memo` จึงตอบสนองต่อการเปลี่ยนแปลงใน URL และเป็น `Result` เพราะพารามิเตอร์หรือควิรีต้องถูกพาร์สจาก URL และอาจถูกต้องหรือไม่ก็ได้

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

เวอร์ชันที่ไม่ระบุชนิดคืนค่า `Memo<ParamsMap>` เช่นเดียวกัน มันเป็น `Memo` เพื่อตอบสนองต่อการเปลี่ยนแปลงใน URL [`ParamsMap`](https://docs.rs/leptos_router/latest/leptos_router/params/struct.ParamsMap.html) ทำงานคล้ายกับแมปชนิดอื่นๆ มาก โดยมีเมธอด `.get()` ที่คืนค่า `Option<String>`

```rust
use leptos_router::hooks::{use_params_map, use_query_map};

let params = use_params_map();
let query = use_query_map();

// id: || -> Option<String>
let id = move || params.read().get("id");
```

เรื่องนี้อาจยุ่งเหยิงสักหน่อย: การสร้างสัญญาณอนุพัทธ์ที่ห่อ `Option<_>` หรือ `Result<_>` อาจมีหลายขั้นตอน แต่ก็คุ้มค่าที่จะทำด้วยเหตุผลสองประการ:

1. มันถูกต้อง กล่าวคือ มันบังคับให้คุณคำนึงถึงกรณีต่างๆ ว่า “ถ้าผู้ใช้ไม่ส่งค่าสำหรับฟิลด์ควิรีนี้ล่ะ? ถ้าพวกเขาส่งค่าที่ไม่ถูกต้องล่ะ?”
2. มันมีประสิทธิภาพ โดยเฉพาะอย่างยิ่ง เมื่อคุณนำทางระหว่างพาธต่างๆ ที่ตรงกับ `<Route/>` เดียวกัน โดยมีเพียงพารามิเตอร์หรือควิรีที่เปลี่ยนไป คุณจะได้รับการอัปเดตแบบละเอียดไปยังส่วนต่างๆ ของแอปได้โดยไม่ต้องเรนเดอร์ใหม่ ตัวอย่างเช่น การนำทางระหว่างผู้ติดต่อต่างๆ ในตัวอย่างรายชื่อผู้ติดต่อของเราทำการอัปเดตแบบเจาะจงที่ฟิลด์ชื่อ (และท้ายที่สุดคือข้อมูลผู้ติดต่อ) โดยไม่ต้องแทนที่หรือเรนเดอร์ `<Contact/>` ที่ห่ออยู่ใหม่ นี่คือสิ่งที่รีแอกทิวิตีแบบละเอียดมีไว้เพื่อ

> นี่คือตัวอย่างเดียวกันกับหัวข้อก่อนหน้า เราเตอร์เป็นระบบที่ผสานรวมกันมากจนสมเหตุสมผลที่จะมอบตัวอย่างเดียวที่เน้นฟีเจอร์หลายอย่าง แม้ว่าเราจะยังไม่ได้อธิบายพวกมันทั้งหมดก็ตาม

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
